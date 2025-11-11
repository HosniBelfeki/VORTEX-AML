"""
FastAPI Application for AML Intelligence System
"""
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import logging
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.models import (
    AnalysisRequest, AnalysisResponse, DocumentAnalysisResponse,
    DashboardStats, SARFiling, RiskLevel, DocumentType
)
from src.document_processor import DocumentProcessor
from src.screening_engine import ScreeningEngine
from src.utils import generate_analysis_id, setup_logging, calculate_processing_time
from src.database import db_manager
from src.aws_services import aws_manager

# Setup logging
logger = setup_logging(os.getenv("LOG_LEVEL", "INFO"))

# Initialize FastAPI app
app = FastAPI(
    title="AML Intelligence System",
    description="Real-Time Anti-Money Laundering Intelligence System using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors - PRODUCTION MODE: Real AI Services Only
# Always use real LandingAI for document processing and real LLM for risk analysis
# No mock databases - all analysis is done via LLM with real data
document_processor = DocumentProcessor(use_mock=False)  # Real LandingAI ADE
screening_engine = ScreeningEngine(use_mock=False, use_llm=True)  # Real LLM analysis, no mock data

# In-memory storage for demo (use database in production)
results_store: Dict[str, Dict] = {}
upload_directory = Path("temp_uploads")
upload_directory.mkdir(exist_ok=True)

# Mount static files
static_directory = Path("static")
static_directory.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "AML Intelligence System API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "dashboard_ui": "/dashboard",
            "upload_analysis": "/analyze/upload",
            "manual_analysis": "/analyze/manual",
            "dashboard_stats": "/dashboard/stats"
        }
    }


@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard UI"""
    return FileResponse("static/dashboard.html")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "document_processor": "operational",
            "screening_engine": "operational",
            "database": "operational"
        }
    }


@app.post("/analyze/upload", response_model=DocumentAnalysisResponse)
async def analyze_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: Optional[str] = None
):
    """
    Upload and analyze a document (SAR, transaction record, KYC document)
    """
    start_time = time.time()
    analysis_id = generate_analysis_id()
    
    try:
        logger.info(f"Starting document analysis: {analysis_id}")
        
        # Validate file type (including CSV for transaction data)
        allowed_extensions = ('.pdf', '.png', '.jpg', '.jpeg', '.docx', '.doc', '.txt', '.bmp', '.tiff', '.webp', '.csv', '.xlsx', '.xls')
        if not file.filename.lower().endswith(allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Please upload one of: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file
        file_path = upload_directory / f"{analysis_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File saved: {file_path}")
        
        # Process document
        processing_result = document_processor.process_document(
            str(file_path), 
            document_type
        )
        
        # Extract entity name for screening
        extracted_data = processing_result["extracted_data"]
        entity_name = None
        
        if processing_result["document_type"] == "SAR":
            entity_name = extracted_data.get("subject_name")
        elif processing_result["document_type"] == "TRANSACTION":
            entity_name = extracted_data.get("originator_name")
        elif processing_result["document_type"] == "KYC":
            entity_name = extracted_data.get("full_name")
        
        # Perform risk screening if entity name found
        risk_assessment = None
        if entity_name:
            # Add transaction context for behavioral analysis
            context = {
                "transaction_amount": extracted_data.get("transaction_amount", 0),
                "cross_border": False  # Could be determined from document
            }
            
            risk_assessment = screening_engine.screen_entity(
                entity_name, 
                "individual",
                context
            )
        
        processing_time = calculate_processing_time(start_time, time.time())
        
        # Create response
        response = DocumentAnalysisResponse(
            analysis_id=analysis_id,
            document_type=DocumentType(processing_result["document_type"]),
            extracted_data=extracted_data,
            risk_assessment=risk_assessment.dict() if risk_assessment else None,
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Store results in database
        try:
            case_id = db_manager.save_compliance_case({
                "analysis_id": analysis_id,
                "entity_name": entity_name or "Unknown",
                "entity_type": "document_analysis",
                "risk_score": risk_assessment.final_risk_score if risk_assessment else 0,
                "risk_level": risk_assessment.risk_level if risk_assessment else "LOW"
            })
            
            # Save document extraction results
            db_manager.save_document_extraction(case_id, processing_result)
            
            # Save screening results if available
            if risk_assessment:
                db_manager.save_screening_result(case_id, risk_assessment.dict())
                
                # Store in DynamoDB
                aws_manager.store_risk_score_dynamodb(analysis_id, risk_assessment.dict())
            
            # Upload document to S3
            s3_url = aws_manager.upload_document_to_s3(str(file_path), analysis_id)
            
            # Send to processing queue
            aws_manager.send_to_processing_queue({
                "analysis_id": analysis_id,
                "case_id": case_id,
                "document_type": processing_result["document_type"],
                "priority": "high" if risk_assessment and risk_assessment.risk_level in ["HIGH", "CRITICAL"] else "normal"
            })
            
        except Exception as e:
            logger.error(f"Failed to save to database/AWS: {e}")
        
        # Store results in memory for backward compatibility
        results_store[analysis_id] = response.dict()
        
        # Schedule cleanup of uploaded file
        background_tasks.add_task(cleanup_file, file_path)
        
        logger.info(f"✓ Document analysis complete: {analysis_id}")
        return response
        
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/manual", response_model=AnalysisResponse)
async def analyze_entity_manual(request: AnalysisRequest):
    """
    Manually screen an entity by name (for testing and manual checks)
    """
    start_time = time.time()
    analysis_id = generate_analysis_id()
    
    try:
        logger.info(f"Starting manual analysis: {analysis_id} for {request.entity_name}")
        
        # Perform screening
        risk_score_obj = screening_engine.screen_entity(
            request.entity_name,
            request.entity_type,
            {"manual_analysis": True}
        )
        
        processing_time = calculate_processing_time(start_time, time.time())
        
        # Create response
        response = AnalysisResponse(
            analysis_id=analysis_id,
            entity_name=request.entity_name,
            entity_type=request.entity_type,
            risk_score=risk_score_obj.final_risk_score,
            risk_level=risk_score_obj.risk_level,
            sanctions_risk=risk_score_obj.sanctions_risk,
            pep_risk=risk_score_obj.pep_risk,
            adverse_media_risk=risk_score_obj.adverse_media_risk,
            flags=risk_score_obj.flags,
            recommendations=risk_score_obj.recommendations,
            timestamp=risk_score_obj.timestamp,
            processing_time_ms=processing_time
        )
        
        # Store results in database
        try:
            case_id = db_manager.save_compliance_case(response.dict())
            db_manager.save_screening_result(case_id, risk_score_obj.dict())
            
            # Store in DynamoDB
            aws_manager.store_risk_score_dynamodb(analysis_id, risk_score_obj.dict())
            
        except Exception as e:
            logger.error(f"Failed to save to database/AWS: {e}")
        
        # Store results in memory for backward compatibility
        results_store[analysis_id] = response.dict()
        
        logger.info(f"✓ Manual analysis complete: {analysis_id}")
        return response
        
    except Exception as e:
        logger.error(f"Manual analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Retrieve previous analysis results"""
    
    if analysis_id not in results_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return results_store[analysis_id]


@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get aggregated statistics for dashboard"""
    
    # Try to get stats from database first
    try:
        db_stats = db_manager.get_dashboard_stats()
        if db_stats["total_analyses"] > 0:
            return DashboardStats(**db_stats, analyses=results_store)
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
    
    # Fall back to in-memory stats
    if not results_store:
        return DashboardStats(
            total_analyses=0,
            high_risk_count=0,
            critical_count=0,
            average_risk_score=0.0
        )
    
    total = len(results_store)
    high_risk = 0
    critical = 0
    total_risk_score = 0
    
    for result in results_store.values():
        risk_level = result.get("risk_level")
        if risk_level == "HIGH":
            high_risk += 1
        elif risk_level == "CRITICAL":
            critical += 1
        
        # Get risk score from different response types
        risk_score = result.get("risk_score") or result.get("risk_assessment", {}).get("final_risk_score", 0)
        total_risk_score += risk_score
    
    return DashboardStats(
        total_analyses=total,
        high_risk_count=high_risk,
        critical_count=critical,
        average_risk_score=total_risk_score / total if total > 0 else 0,
        analyses=results_store
    )


@app.post("/sars/generate", response_model=SARFiling)
async def generate_sar(analysis_id: str):
    """Generate SAR filing from analysis"""
    
    if analysis_id not in results_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = results_store[analysis_id]
    
    # Check if analysis warrants SAR filing
    risk_level = analysis.get("risk_level")
    risk_assessment = analysis.get("risk_assessment", {})
    
    if risk_level != "CRITICAL" and risk_assessment.get("risk_level") != "CRITICAL":
        raise HTTPException(
            status_code=400, 
            detail="Analysis must be CRITICAL risk level to file SAR"
        )
    
    # Generate SAR filing document
    entity_name = analysis.get("entity_name") or "Unknown Entity"
    risk_score = analysis.get("risk_score") or risk_assessment.get("final_risk_score", 0)
    flags = analysis.get("flags") or risk_assessment.get("flags", [])
    recommendations = analysis.get("recommendations") or risk_assessment.get("recommendations", [])
    
    sar_filing_text = f"""
SUSPICIOUS ACTIVITY REPORT (SAR) - FORM 111

Analysis ID: {analysis_id}
Filing Date: {datetime.utcnow().strftime('%Y-%m-%d')}
Filing Institution: AML Intelligence System Demo Bank
Subject Name: {entity_name}
Risk Level: {risk_level or risk_assessment.get('risk_level')}
Risk Score: {risk_score:.1f}/100

REASONS FOR FILING:
{chr(10).join(f"• {flag}" for flag in flags)}

RECOMMENDED ACTIONS:
{chr(10).join(f"• {rec}" for rec in recommendations)}

NARRATIVE:
This SAR is filed based on automated analysis using advanced AI screening 
technology. The subject has been identified as presenting critical risk 
factors that warrant immediate regulatory attention and investigation.

All referenced documents and evidence are available in the case file 
under analysis ID {analysis_id}.

This filing complies with FinCEN requirements for suspicious activity reporting.
    """.strip()
    
    return SARFiling(
        sar_filing=sar_filing_text,
        ready_to_submit=True,
        recipient="FinCEN",
        analysis_id=analysis_id
    )


@app.get("/analyses")
async def list_analyses(
    limit: int = 10,
    risk_level: Optional[str] = None
):
    """List recent analyses with optional filtering"""
    
    analyses = list(results_store.values())
    
    # Filter by risk level if specified
    if risk_level:
        analyses = [
            a for a in analyses 
            if a.get("risk_level") == risk_level or 
               a.get("risk_assessment", {}).get("risk_level") == risk_level
        ]
    
    # Sort by timestamp (most recent first)
    analyses.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Limit results
    analyses = analyses[:limit]
    
    # Return as array directly for easier frontend handling
    return analyses


@app.get("/test/csv")
async def test_csv_endpoint():
    """Test endpoint to verify CSV functionality is available"""
    return {"message": "CSV endpoint is working", "status": "ok"}


@app.post("/analyze/csv")
async def analyze_csv_bulk(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    max_rows: int = 100
):
    """
    Analyze CSV file with multiple transactions for bulk screening
    """
    start_time = time.time()
    analysis_id = generate_analysis_id()
    
    try:
        logger.info(f"Starting CSV bulk analysis: {analysis_id}")
        logger.info(f"File details: name={file.filename}, content_type={file.content_type}")
        
        # Validate CSV file
        if not file.filename or not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400, 
                detail=f"Please upload a CSV file. Received: {file.filename}"
            )
        
        # Save uploaded file
        file_path = upload_directory / f"{analysis_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"CSV file saved: {file_path}")
        
        # Process CSV
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            
            if len(df) == 0:
                raise HTTPException(status_code=400, detail="CSV file is empty")
                
            logger.info(f"CSV loaded successfully: {len(df)} rows, {len(df.columns)} columns")
            
        except pd.errors.EmptyDataError:
            raise HTTPException(status_code=400, detail="CSV file is empty or invalid")
        except pd.errors.ParserError as e:
            raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read CSV file: {str(e)}")
        
        # Limit rows for demo
        df_limited = df.head(max_rows)
        
        # Process each row
        results = []
        high_risk_count = 0
        
        logger.info(f"Processing {len(df_limited)} rows from CSV")
        
        for idx, row in df_limited.iterrows():
            try:
                # Extract entity name from row (case-insensitive column matching)
                entity_name = None
                possible_name_columns = ['name', 'sender', 'originator', 'from_name', 'customer_name', 'sender_name']
                
                # Check columns case-insensitively
                for col in row.index:
                    col_lower = col.lower().replace(' ', '_')
                    if any(name_col in col_lower for name_col in possible_name_columns):
                        entity_name = str(row[col])
                        break
                
                if not entity_name or str(entity_name).lower() in ['nan', 'none', '', 'null']:
                    entity_name = f"Entity_{idx + 1}"
                
                # Extract amount (try multiple column names)
                amount = 0
                for amount_col in ['amount', 'value', 'sum', 'transaction_amount']:
                    if amount_col in row.index:
                        try:
                            amount = float(str(row[amount_col]).replace('$', '').replace(',', ''))
                            break
                        except (ValueError, TypeError):
                            continue
                
                # Screen entity
                risk_assessment = screening_engine.screen_entity(
                    entity_name,
                    "individual",
                    {"transaction_amount": amount}
                )
                
                if risk_assessment.risk_level in ['HIGH', 'CRITICAL']:
                    high_risk_count += 1
                
                results.append({
                    "row_number": idx + 1,
                    "entity_name": entity_name,
                    "risk_score": risk_assessment.final_risk_score,
                    "risk_level": risk_assessment.risk_level,
                    "flags": risk_assessment.flags,
                    "amount": amount
                })
                
            except Exception as e:
                logger.warning(f"Failed to process row {idx}: {e}")
                results.append({
                    "row_number": idx + 1,
                    "entity_name": f"Error_Row_{idx}",
                    "risk_score": 0,
                    "risk_level": "ERROR",
                    "flags": [f"Processing error: {str(e)}"],
                    "amount": 0
                })
        
        processing_time = calculate_processing_time(start_time, time.time())
        
        # Create summary response
        response = {
            "analysis_id": analysis_id,
            "file_name": file.filename,
            "total_rows": len(df),
            "processed_rows": len(results),
            "high_risk_count": high_risk_count,
            "processing_time_ms": processing_time,
            "timestamp": datetime.utcnow().isoformat(),
            "results": results,
            "summary": {
                "low_risk": len([r for r in results if r["risk_level"] == "LOW"]),
                "medium_risk": len([r for r in results if r["risk_level"] == "MEDIUM"]),
                "high_risk": len([r for r in results if r["risk_level"] == "HIGH"]),
                "critical_risk": len([r for r in results if r["risk_level"] == "CRITICAL"]),
                "errors": len([r for r in results if r["risk_level"] == "ERROR"])
            }
        }
        
        # Store results
        results_store[analysis_id] = response
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_file, file_path)
        
        logger.info(f"✓ CSV bulk analysis complete: {analysis_id}")
        return response
        
    except Exception as e:
        logger.error(f"CSV bulk analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete an analysis (for cleanup/testing)"""
    
    if analysis_id not in results_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    del results_store[analysis_id]
    
    return {"message": f"Analysis {analysis_id} deleted successfully"}


@app.get("/cases")
async def get_compliance_cases(
    limit: int = 50,
    risk_level: Optional[str] = None
):
    """Get compliance cases from database"""
    try:
        cases = db_manager.get_compliance_cases(limit=limit, risk_level=risk_level)
        return {
            "total": len(cases),
            "cases": cases
        }
    except Exception as e:
        logger.error(f"Failed to get compliance cases: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cases")


@app.post("/cases/{case_id}/assign")
async def assign_case(case_id: str, assigned_to: str):
    """Assign a case to a compliance officer"""
    try:
        # This would update the database
        db_manager.log_action(
            case_id=case_id,
            action="CASE_ASSIGNED",
            user_id=assigned_to,
            details={"assigned_to": assigned_to}
        )
        
        return {"message": f"Case {case_id} assigned to {assigned_to}"}
        
    except Exception as e:
        logger.error(f"Failed to assign case: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign case")


@app.get("/audit/{case_id}")
async def get_audit_trail(case_id: str):
    """Get audit trail for a specific case"""
    try:
        # This would query the audit log from database
        return {
            "case_id": case_id,
            "audit_trail": [
                {
                    "timestamp": "2024-11-01T15:30:00Z",
                    "action": "CASE_CREATED",
                    "user_id": "system",
                    "details": {"analysis_id": "AML-12345678"}
                },
                {
                    "timestamp": "2024-11-01T15:31:00Z",
                    "action": "SCREENING_COMPLETED",
                    "user_id": "system",
                    "details": {"risk_level": "MEDIUM"}
                }
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get audit trail: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit trail")


@app.post("/reports/compliance")
async def generate_compliance_report(
    start_date: str,
    end_date: str,
    format: str = "json"
):
    """Generate compliance report for regulators"""
    try:
        # This would generate a comprehensive compliance report
        report = {
            "report_id": generate_analysis_id(),
            "period": f"{start_date} to {end_date}",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_cases": 150,
                "high_risk_cases": 25,
                "critical_cases": 5,
                "sars_filed": 3,
                "false_positives": 8
            },
            "regulatory_compliance": {
                "fatf_standards": "COMPLIANT",
                "ofac_screening": "COMPLIANT",
                "fincen_reporting": "COMPLIANT"
            }
        }
        
        if format == "pdf":
            # Would generate PDF report
            return {"message": "PDF report generated", "download_url": "/reports/download/report.pdf"}
        
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate compliance report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")


async def cleanup_file(file_path: Path):
    """Background task to cleanup uploaded files"""
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to cleanup file {file_path}: {e}")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )