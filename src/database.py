"""
Database integration for AML Intelligence System
"""
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aml_system.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ComplianceCase(Base):
    """Compliance cases table"""
    __tablename__ = "compliance_cases"
    
    case_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String, unique=True, nullable=False)
    entity_name = Column(String(255), nullable=False)
    entity_type = Column(String(50), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    status = Column(String(50), default='pending_review')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_to = Column(String(255))
    notes = Column(Text)


class DocumentExtraction(Base):
    """Document extraction results"""
    __tablename__ = "document_extractions"
    
    extraction_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, nullable=False)
    document_type = Column(String(50), nullable=False)
    extracted_data = Column(Text, nullable=False)  # JSON as text for SQLite compatibility
    confidence_scores = Column(Text, nullable=False)  # JSON as text
    extraction_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class ScreeningResult(Base):
    """Screening results"""
    __tablename__ = "screening_results"
    
    screening_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, nullable=False)
    sanctions_risk = Column(Float)
    pep_risk = Column(Float)
    adverse_media_risk = Column(Float)
    behavioral_risk = Column(Float)
    flags = Column(Text, nullable=False)  # JSON as text
    recommendations = Column(Text, nullable=False)  # JSON as text
    created_at = Column(DateTime, default=datetime.utcnow)


class SARFiling(Base):
    """SAR filings"""
    __tablename__ = "sar_filings"
    
    sar_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, nullable=False)
    filing_date = Column(DateTime, nullable=False)
    filed_by = Column(String(255), nullable=False)
    financial_institution = Column(String(255), nullable=False)
    sar_document = Column(Text, nullable=False)
    status = Column(String(50), default='drafted')
    fincen_receipt_number = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Audit trail"""
    __tablename__ = "audit_log"
    
    log_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String)
    action = Column(String(255), nullable=False)
    user_id = Column(String(255))
    details = Column(Text)  # JSON as text
    timestamp = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        
    def create_tables(self):
        """Create all tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✓ Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def save_compliance_case(self, analysis_data: Dict) -> str:
        """Save compliance case to database"""
        session = self.get_session()
        try:
            case = ComplianceCase(
                analysis_id=analysis_data["analysis_id"],
                entity_name=analysis_data["entity_name"],
                entity_type=analysis_data["entity_type"],
                risk_score=analysis_data["risk_score"],
                risk_level=analysis_data["risk_level"]
            )
            session.add(case)
            session.commit()
            
            # Log the action
            self.log_action(
                case_id=case.case_id,
                action="CASE_CREATED",
                details={"analysis_id": analysis_data["analysis_id"]}
            )
            
            logger.info(f"✓ Saved compliance case: {case.case_id}")
            return case.case_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save compliance case: {e}")
            raise
        finally:
            session.close()
    
    def save_screening_result(self, case_id: str, screening_data: Dict):
        """Save screening results to database"""
        session = self.get_session()
        try:
            import json
            
            result = ScreeningResult(
                case_id=case_id,
                sanctions_risk=screening_data.get("sanctions_risk", 0),
                pep_risk=screening_data.get("pep_risk", 0),
                adverse_media_risk=screening_data.get("adverse_media_risk", 0),
                behavioral_risk=screening_data.get("behavioral_risk", 0),
                flags=json.dumps(screening_data.get("flags", [])),
                recommendations=json.dumps(screening_data.get("recommendations", []))
            )
            session.add(result)
            session.commit()
            
            logger.info(f"✓ Saved screening result for case: {case_id}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save screening result: {e}")
            raise
        finally:
            session.close()
    
    def save_document_extraction(self, case_id: str, extraction_data: Dict):
        """Save document extraction results"""
        session = self.get_session()
        try:
            import json
            
            extraction = DocumentExtraction(
                case_id=case_id,
                document_type=extraction_data["document_type"],
                extracted_data=json.dumps(extraction_data["extracted_data"]),
                confidence_scores=json.dumps(extraction_data.get("confidence_scores", {})),
                extraction_time_ms=extraction_data.get("processing_time_ms", 0)
            )
            session.add(extraction)
            session.commit()
            
            logger.info(f"✓ Saved document extraction for case: {case_id}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save document extraction: {e}")
            raise
        finally:
            session.close()
    
    def get_compliance_cases(self, limit: int = 50, risk_level: str = None) -> List[Dict]:
        """Get compliance cases with optional filtering"""
        session = self.get_session()
        try:
            query = session.query(ComplianceCase)
            
            if risk_level:
                query = query.filter(ComplianceCase.risk_level == risk_level)
            
            cases = query.order_by(ComplianceCase.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "case_id": case.case_id,
                    "analysis_id": case.analysis_id,
                    "entity_name": case.entity_name,
                    "entity_type": case.entity_type,
                    "risk_score": case.risk_score,
                    "risk_level": case.risk_level,
                    "status": case.status,
                    "created_at": case.created_at.isoformat(),
                    "assigned_to": case.assigned_to,
                    "notes": case.notes
                }
                for case in cases
            ]
            
        except Exception as e:
            logger.error(f"Failed to get compliance cases: {e}")
            return []
        finally:
            session.close()
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics from database"""
        session = self.get_session()
        try:
            total_cases = session.query(ComplianceCase).count()
            high_risk = session.query(ComplianceCase).filter(
                ComplianceCase.risk_level == "HIGH"
            ).count()
            critical_risk = session.query(ComplianceCase).filter(
                ComplianceCase.risk_level == "CRITICAL"
            ).count()
            
            # Calculate average risk score
            avg_risk = session.query(ComplianceCase.risk_score).all()
            avg_risk_score = sum(r[0] for r in avg_risk) / len(avg_risk) if avg_risk else 0
            
            return {
                "total_analyses": total_cases,
                "high_risk_count": high_risk,
                "critical_count": critical_risk,
                "average_risk_score": avg_risk_score
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            return {
                "total_analyses": 0,
                "high_risk_count": 0,
                "critical_count": 0,
                "average_risk_score": 0.0
            }
        finally:
            session.close()
    
    def log_action(self, case_id: str = None, action: str = "", user_id: str = None, details: Dict = None):
        """Log an action to audit trail"""
        session = self.get_session()
        try:
            import json
            
            log_entry = AuditLog(
                case_id=case_id,
                action=action,
                user_id=user_id,
                details=json.dumps(details or {})
            )
            session.add(log_entry)
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to log action: {e}")
        finally:
            session.close()
    
    def create_sar_filing(self, case_id: str, sar_data: Dict) -> str:
        """Create SAR filing record"""
        session = self.get_session()
        try:
            sar = SARFiling(
                case_id=case_id,
                filing_date=datetime.utcnow(),
                filed_by=sar_data.get("filed_by", "AML System"),
                financial_institution=sar_data.get("institution", "Demo Bank"),
                sar_document=sar_data["sar_filing"]
            )
            session.add(sar)
            session.commit()
            
            # Log the SAR filing
            self.log_action(
                case_id=case_id,
                action="SAR_FILED",
                details={"sar_id": sar.sar_id}
            )
            
            logger.info(f"✓ Created SAR filing: {sar.sar_id}")
            return sar.sar_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create SAR filing: {e}")
            raise
        finally:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()

# Initialize database on import
try:
    db_manager.create_tables()
except Exception as e:
    logger.warning(f"Database initialization failed: {e}")
    logger.info("Using in-memory storage for demo")