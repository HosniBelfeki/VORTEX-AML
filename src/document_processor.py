"""
Document Processing Engine using LandingAI ADE
"""
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging
from src.models import SuspiciousActivityReport, TransactionRecord, KYCDocument, DocumentType
from src.utils import mock_bedrock_extraction, generate_analysis_id
from src.aws_services import aws_manager

logger = logging.getLogger(__name__)


class MockLandingAIADE:
    """
    Mock LandingAI ADE client for demo purposes
    In production, replace with actual LandingAI ADE client
    """
    
    def __init__(self, apikey: str = None, environment: str = "production"):
        self.apikey = apikey
        self.environment = environment
        logger.info("Initialized Mock LandingAI ADE client")
    
    def parse(self, document: Union[str, Path], model: str = "dpt-2-latest"):
        """Mock document parsing"""
        logger.info(f"Mock parsing document: {document}")
        
        # Simulate processing time
        time.sleep(0.5)
        
        # Return mock response with markdown content
        class MockResponse:
            def __init__(self):
                self.markdown = """
                # Document Content
                
                This is mock extracted content from the document.
                The actual LandingAI ADE would extract structured data here.
                
                ## Key Information
                - Names: John Smith
                - Amounts: $150,000
                - Dates: 2024-10-15
                """
                self.chunks = ["chunk1", "chunk2", "chunk3"]
        
        return MockResponse()


class DocumentProcessor:
    """Main document processor using LandingAI ADE"""
    
    def __init__(self, api_key: Optional[str] = None, use_mock: bool = False):
        """
        Initialize document processor
        
        Args:
            api_key: LandingAI API key
            use_mock: Use mock implementation for demo (default: False - use real services)
        """
        self.use_mock = use_mock
        self.use_real_bedrock = False
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        if use_mock:
            self.client = MockLandingAIADE(apikey=api_key)
            logger.info("📝 Using mock LandingAI ADE client")
        else:
            # In production, use actual LandingAI ADE client
            try:
                from landingai_ade import LandingAIADE
                
                # Try multiple API key environment variables
                landing_ai_key = (
                    api_key or 
                    os.getenv("LANDING_AI_API_KEY") or 
                    os.getenv("VISION_AGENT_API_KEY")
                )
                
                if not landing_ai_key:
                    raise ValueError("No LandingAI API key found in environment")
                
                self.client = LandingAIADE(apikey=landing_ai_key)
                logger.info("✅ Real LandingAI ADE client initialized")
            except ImportError:
                logger.warning("⚠️ LandingAI ADE not available, using mock implementation")
                self.client = MockLandingAIADE(apikey=api_key)
                self.use_mock = True
            except Exception as e:
                logger.warning(f"⚠️ LandingAI ADE initialization failed: {e}, using mock implementation")
                self.client = MockLandingAIADE(apikey=api_key)
                self.use_mock = True
        
        # Check if AWS Bedrock is available
        if self._has_aws_credentials():
            self.use_real_bedrock = True
            logger.info("✅ AWS Bedrock available for LLM analysis")
        else:
            logger.info("📝 AWS Bedrock not configured, using mock extraction")
    
    def process_document(self, document_path: str, document_type: str = None) -> Dict:
        """
        Process any document and return extracted data
        
        Args:
            document_path: Path to document file
            document_type: Type of document (SAR, TRANSACTION, KYC)
        
        Returns:
            Dictionary with extracted data and metadata
        """
        start_time = time.time()
        
        logger.info(f"Processing document: {document_path}")
        
        # Auto-detect document type if not provided
        if not document_type:
            from src.utils import validate_document_type
            document_type = validate_document_type(document_path)
        
        # Check if it's a CSV file for direct processing
        if document_path.lower().endswith('.csv'):
            extracted_data = self._process_csv_file(document_path, document_type)
        else:
            # Parse document using LandingAI ADE (or mock)
            response = self.client.parse(
                document=Path(document_path),
                model="dpt-2-latest"
            )
            
            # Extract structured data using Bedrock (or mock)
            extracted_data = self._extract_structured_data(
                document_type=document_type,
                markdown_content=response.markdown
            )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # Create appropriate data model
        if document_type == "SAR":
            document_obj = SuspiciousActivityReport(**extracted_data)
        elif document_type == "TRANSACTION":
            document_obj = TransactionRecord(**extracted_data)
        elif document_type == "KYC":
            document_obj = KYCDocument(**extracted_data)
        else:
            raise ValueError(f"Unsupported document type: {document_type}")
        
        logger.info(f"✓ Successfully processed {document_type} document in {processing_time}ms")
        
        return {
            "document_type": document_type,
            "extracted_data": document_obj.dict(),
            "processing_time_ms": processing_time,
            "analysis_id": generate_analysis_id()
        }
    
    def extract_sar_data(self, document_path: str) -> SuspiciousActivityReport:
        """Extract data from Suspicious Activity Report (SAR) forms"""
        result = self.process_document(document_path, "SAR")
        return SuspiciousActivityReport(**result["extracted_data"])
    
    def extract_transaction_data(self, document_path: str) -> TransactionRecord:
        """Extract data from transaction records"""
        result = self.process_document(document_path, "TRANSACTION")
        return TransactionRecord(**result["extracted_data"])
    
    def extract_kyc_data(self, document_path: str) -> KYCDocument:
        """Extract data from KYC documents"""
        result = self.process_document(document_path, "KYC")
        return KYCDocument(**result["extracted_data"])
    
    def _extract_structured_data(self, document_type: str, markdown_content: str) -> Dict:
        """
        Extract structured data using Bedrock Claude or mock implementation
        """
        
        if self.use_mock or not self.use_real_bedrock:
            # Use mock extraction for demo
            logger.info("📝 Using mock extraction")
            return mock_bedrock_extraction(document_type, markdown_content)
        
        # Use real AWS Bedrock LLM
        logger.info("🤖 Using AWS Bedrock Claude for extraction")
        try:
            return self._extract_with_bedrock(document_type, markdown_content)
        except Exception as e:
            logger.error(f"❌ Bedrock extraction failed: {e}, falling back to mock")
            return mock_bedrock_extraction(document_type, markdown_content)
    
    def _extract_with_bedrock(self, document_type: str, markdown_content: str) -> Dict:
        """Use Bedrock Claude to intelligently extract structured data"""
        
        try:
            import boto3
            
            bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
            
            # Create extraction prompt based on document type
            prompts = {
                "SAR": """Extract the following information from the SAR form and return as JSON:
                - report_id: The SAR report ID/number
                - filing_date: Date the SAR was filed
                - filing_institution: Bank/institution filing the SAR
                - subject_name: Name of the suspicious subject
                - subject_account: Account number involved
                - transaction_amount: Amount of suspicious transaction
                - transaction_date: Date of transaction
                - suspicious_activity_type: Type of suspicious activity
                - narrative: Summary of suspicious activity
                
                Document content:
                {content}
                
                Return only valid JSON with these fields and confidence_scores.""",
                
                "TRANSACTION": """Extract transaction details and return as JSON:
                - transaction_id: Unique transaction ID
                - transaction_date: Date of transaction
                - originator_name: Name of sender
                - originator_account: Sender account number
                - beneficiary_name: Name of receiver
                - beneficiary_account: Receiver account number
                - amount: Transaction amount
                - currency: Currency (USD, EUR, etc.)
                - purpose: Purpose of transaction
                
                Document content:
                {content}
                
                Return only valid JSON with these fields and confidence_scores.""",
                
                "KYC": """Extract KYC document information and return as JSON:
                - customer_id: Customer ID if available
                - full_name: Full legal name
                - date_of_birth: DOB in YYYY-MM-DD format
                - nationality: Country of citizenship
                - document_type: Type of ID document
                - document_number: ID document number
                - issue_date: Date issued
                - expiry_date: Date expires
                - address: Current address
                - politically_exposed_person: boolean
                
                Document content:
                {content}
                
                Return only valid JSON with these fields and confidence_scores."""
            }
            
            prompt = prompts.get(document_type, "")
            
            # Call Bedrock Claude with updated model
            response = bedrock_client.invoke_model(
                modelId="anthropic.claude-sonnet-4-5-20250929-v1:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-06-01",
                    "max_tokens": 1024,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt.format(content=markdown_content)
                        }
                    ]
                })
            )
            
            response_body = json.loads(response['body'].read())
            response_text = response_body['content'][0]['text']
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            extracted_data = json.loads(json_str)
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Bedrock extraction failed: {e}")
            # Fall back to mock extraction
            return mock_bedrock_extraction(document_type, markdown_content)
    
    def _process_csv_file(self, csv_path: str, document_type: str) -> Dict:
        """Process CSV file directly without LandingAI"""
        try:
            import pandas as pd
            
            # Read CSV file
            df = pd.read_csv(csv_path)
            logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Get first row as sample (or aggregate if multiple rows)
            if len(df) == 0:
                raise ValueError("CSV file is empty")
            
            # Take first row for single transaction analysis
            first_row = df.iloc[0].to_dict()
            
            # Map CSV columns to expected transaction fields
            extracted_data = self._map_csv_to_transaction(first_row, df)
            
            # Add confidence scores
            extracted_data["confidence_scores"] = {
                key: 0.95 for key in extracted_data.keys() 
                if key != "confidence_scores"
            }
            
            logger.info(f"✓ CSV processed: {len(df)} transactions found")
            return extracted_data
            
        except Exception as e:
            logger.error(f"CSV processing failed: {e}")
            # Fall back to mock data
            return mock_bedrock_extraction(document_type, f"CSV file with error: {e}")
    
    def _map_csv_to_transaction(self, first_row: Dict, df) -> Dict:
        """Map CSV columns to transaction record format"""
        
        # Common CSV column mappings (flexible)
        column_mappings = {
            'transaction_id': ['id', 'transaction_id', 'txn_id', 'reference', 'ref'],
            'transaction_date': ['date', 'transaction_date', 'txn_date', 'timestamp'],
            'originator_name': ['from', 'sender', 'originator', 'from_name', 'sender_name'],
            'originator_account': ['from_account', 'sender_account', 'orig_account'],
            'beneficiary_name': ['to', 'receiver', 'beneficiary', 'to_name', 'receiver_name'],
            'beneficiary_account': ['to_account', 'receiver_account', 'ben_account'],
            'amount': ['amount', 'value', 'sum', 'transaction_amount'],
            'currency': ['currency', 'curr', 'ccy'],
            'purpose': ['purpose', 'description', 'memo', 'reference', 'details']
        }
        
        # Map columns
        mapped_data = {}
        csv_columns = [col.lower().replace(' ', '_') for col in first_row.keys()]
        
        for field, possible_columns in column_mappings.items():
            value = None
            
            # Try to find matching column
            for possible_col in possible_columns:
                for csv_col, csv_value in first_row.items():
                    if possible_col in csv_col.lower().replace(' ', '_'):
                        value = csv_value
                        break
                if value is not None:
                    break
            
            # Set default values if not found
            if value is None:
                if field == 'transaction_id':
                    value = f"CSV-{hash(str(first_row)) % 100000}"
                elif field == 'transaction_date':
                    value = datetime.utcnow().strftime('%Y-%m-%d')
                elif field == 'currency':
                    value = "USD"
                elif field in ['originator_name', 'beneficiary_name']:
                    value = "Unknown Entity"
                elif field in ['originator_account', 'beneficiary_account']:
                    value = "Unknown Account"
                elif field == 'amount':
                    # Try to find any numeric column
                    for csv_value in first_row.values():
                        try:
                            value = float(str(csv_value).replace('$', '').replace(',', ''))
                            break
                        except:
                            continue
                    if value is None:
                        value = 0.0
                else:
                    value = "Not specified"
            
            mapped_data[field] = value
        
        # Add CSV metadata
        mapped_data['csv_rows_count'] = len(df)
        mapped_data['csv_columns'] = list(df.columns)
        
        return mapped_data

    def _has_aws_credentials(self) -> bool:
        """Check if AWS credentials are available"""
        try:
            import boto3
            session = boto3.Session()
            credentials = session.get_credentials()
            return credentials is not None
        except:
            return False


# Example usage
if __name__ == "__main__":
    processor = DocumentProcessor(use_mock=True)
    
    # This would work with actual document files
    # result = processor.process_document("sample_sar.pdf", "SAR")
    # print(f"Processed document: {result['analysis_id']}")
    
    print("Document processor initialized successfully")