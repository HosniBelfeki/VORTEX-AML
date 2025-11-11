"""
Utility functions for AML Intelligence System
"""
import uuid
import logging
from difflib import SequenceMatcher
from typing import Dict, Any
import json


def generate_analysis_id() -> str:
    """Generate unique analysis ID"""
    return f"AML-{uuid.uuid4().hex[:8].upper()}"


def fuzzy_match(name1: str, name2: str) -> float:
    """Calculate fuzzy string similarity between two names"""
    return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def mock_bedrock_extraction(document_type: str, content: str) -> Dict[str, Any]:
    """
    Mock Bedrock extraction for demo purposes
    In production, this would call actual AWS Bedrock API
    """
    
    # Mock extracted data based on document type
    if document_type == "SAR":
        return {
            "report_id": "SAR-2024-001234",
            "filing_date": "2024-11-01",
            "filing_institution": "First National Bank",
            "subject_name": "John Smith",
            "subject_account": "ACC-9876543",
            "transaction_amount": 150000.0,
            "transaction_date": "2024-10-15",
            "suspicious_activity_type": "Structuring - Below Reporting Threshold",
            "narrative": "Customer made 5 structured deposits of $9,900 each within 3-day period to avoid $10K reporting threshold.",
            "confidence_scores": {
                "report_id": 0.99,
                "filing_date": 0.98,
                "subject_name": 0.95,
                "transaction_amount": 0.97
            }
        }
    
    elif document_type == "TRANSACTION":
        return {
            "transaction_id": "TXN-789012",
            "transaction_date": "2024-10-15",
            "originator_name": "John Smith",
            "originator_account": "ACC-9876543",
            "beneficiary_name": "Shell Company LLC",
            "beneficiary_account": "ACC-1234567",
            "amount": 50000.0,
            "currency": "USD",
            "purpose": "Business services",
            "confidence_scores": {
                "transaction_id": 0.98,
                "originator_name": 0.96,
                "amount": 0.99
            }
        }
    
    elif document_type == "KYC":
        return {
            "customer_id": "CUST-456789",
            "full_name": "John Smith",
            "date_of_birth": "1980-05-15",
            "nationality": "US",
            "document_type": "Passport",
            "document_number": "P123456789",
            "issue_date": "2020-01-01",
            "expiry_date": "2030-01-01",
            "address": "123 Main St, New York, NY 10001",
            "politically_exposed_person": False,
            "confidence_scores": {
                "full_name": 0.98,
                "date_of_birth": 0.95,
                "document_number": 0.99
            }
        }
    
    return {}


def validate_document_type(filename: str) -> str:
    """Determine document type from filename"""
    filename_lower = filename.lower()
    
    if "sar" in filename_lower or "suspicious" in filename_lower:
        return "SAR"
    elif "transaction" in filename_lower or "wire" in filename_lower or "transfer" in filename_lower or filename_lower.endswith('.csv'):
        return "TRANSACTION"  # CSV files are typically transaction data
    elif "kyc" in filename_lower or "passport" in filename_lower or "id" in filename_lower:
        return "KYC"
    else:
        return "TRANSACTION"  # Default CSV to transaction type


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount for display"""
    if currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def calculate_processing_time(start_time: float, end_time: float) -> int:
    """Calculate processing time in milliseconds"""
    return int((end_time - start_time) * 1000)