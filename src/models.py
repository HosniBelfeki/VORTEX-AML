"""
Data models for AML Intelligence System
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DocumentType(str, Enum):
    SAR = "SAR"
    TRANSACTION = "TRANSACTION"
    KYC = "KYC"


class SuspiciousActivityReport(BaseModel):
    """Suspicious Activity Report data model"""
    report_id: str
    filing_date: str
    filing_institution: str
    subject_name: str
    subject_account: str
    transaction_amount: float
    transaction_date: str
    suspicious_activity_type: str
    narrative: str
    confidence_scores: Dict[str, float] = Field(default_factory=dict)


class TransactionRecord(BaseModel):
    """Transaction record data model"""
    transaction_id: str
    transaction_date: str
    originator_name: str
    originator_account: str
    beneficiary_name: str
    beneficiary_account: str
    amount: float
    currency: str = "USD"
    purpose: str
    confidence_scores: Dict[str, float] = Field(default_factory=dict)


class KYCDocument(BaseModel):
    """KYC document data model"""
    customer_id: str
    full_name: str
    date_of_birth: str
    nationality: str
    document_type: str
    document_number: str
    issue_date: str
    expiry_date: str
    address: str
    politically_exposed_person: bool = False
    confidence_scores: Dict[str, float] = Field(default_factory=dict)


class RiskScore(BaseModel):
    """Risk assessment result"""
    sanctions_risk: float = Field(ge=0, le=100)
    pep_risk: float = Field(ge=0, le=100)
    adverse_media_risk: float = Field(ge=0, le=100)
    behavioral_risk: float = Field(ge=0, le=100)
    final_risk_score: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    flags: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AnalysisRequest(BaseModel):
    """Request model for manual analysis"""
    entity_name: str
    entity_type: str = "individual"
    additional_info: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    analysis_id: str
    entity_name: str
    entity_type: str
    risk_score: float
    risk_level: RiskLevel
    sanctions_risk: float
    pep_risk: float
    adverse_media_risk: float
    flags: List[str]
    recommendations: List[str]
    timestamp: str
    processing_time_ms: Optional[int] = None


class DocumentAnalysisResponse(BaseModel):
    """Response model for document analysis"""
    analysis_id: str
    document_type: DocumentType
    extracted_data: Dict
    risk_assessment: RiskScore
    processing_time_ms: int
    timestamp: str


class DashboardStats(BaseModel):
    """Dashboard statistics model"""
    total_analyses: int
    high_risk_count: int
    critical_count: int
    average_risk_score: float
    analyses: Dict = Field(default_factory=dict)


class SARFiling(BaseModel):
    """SAR filing document model"""
    sar_filing: str
    ready_to_submit: bool
    recipient: str = "FinCEN"
    analysis_id: str
    filing_date: str = Field(default_factory=lambda: datetime.utcnow().isoformat())