"""
AWS Services Integration for AML Intelligence System
"""
import os
import json
import boto3
import logging
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class AWSServiceManager:
    """Manages AWS service integrations"""
    
    def __init__(self, region: str = None):
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.s3_bucket = os.getenv("S3_BUCKET_NAME", f"aml-documents-{int(datetime.now().timestamp())}")
        
        # Initialize AWS clients
        try:
            self.s3_client = boto3.client('s3', region_name=self.region)
            self.bedrock_client = boto3.client('bedrock-runtime', region_name=self.region)
            self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
            self.sqs_client = boto3.client('sqs', region_name=self.region)
            
            logger.info(f"✓ AWS services initialized in region: {self.region}")
            
        except Exception as e:
            logger.warning(f"AWS services initialization failed: {e}")
            self.s3_client = None
            self.bedrock_client = None
            self.dynamodb = None
            self.sqs_client = None
    
    def upload_document_to_s3(self, file_path: str, analysis_id: str) -> Optional[str]:
        """Upload document to S3 and return URL"""
        if not self.s3_client:
            logger.warning("S3 client not available")
            return None
        
        try:
            # Create bucket if it doesn't exist
            try:
                self.s3_client.head_bucket(Bucket=self.s3_bucket)
            except:
                # Create bucket with proper location constraint
                if self.region == 'us-east-1':
                    self.s3_client.create_bucket(Bucket=self.s3_bucket)
                else:
                    self.s3_client.create_bucket(
                        Bucket=self.s3_bucket,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
                
                logger.info(f"Created S3 bucket: {self.s3_bucket}")
            
            # Upload file
            key = f"documents/{analysis_id}/{Path(file_path).name}"
            
            self.s3_client.upload_file(
                file_path,
                self.s3_bucket,
                key,
                ExtraArgs={
                    'Metadata': {
                        'analysis_id': analysis_id,
                        'upload_time': datetime.utcnow().isoformat()
                    }
                }
            )
            
            # Generate presigned URL (valid for 1 hour)
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.s3_bucket, 'Key': key},
                ExpiresIn=3600
            )
            
            logger.info(f"✓ Document uploaded to S3: {key}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload document to S3: {e}")
            return None
    
    def extract_with_bedrock(self, document_type: str, content: str) -> Dict:
        """Use Bedrock Claude for intelligent data extraction"""
        if not self.bedrock_client:
            logger.warning("Bedrock client not available, using mock extraction")
            return self._mock_bedrock_extraction(document_type, content)
        
        try:
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
            
            # Call Bedrock Claude
          response = self.bedrock_client.invoke_model(
    modelId="anthropic.claude-sonnet-4-5-20250929-v1:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-06-01",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": prompt.format(content=content)
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
            
            logger.info(f"✓ Bedrock extraction successful for {document_type}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Bedrock extraction failed: {e}")
            # Fall back to mock extraction
            return self._mock_bedrock_extraction(document_type, content)
    
    def _mock_bedrock_extraction(self, document_type: str, content: str) -> Dict:
        """Mock Bedrock extraction for demo purposes"""
        
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
                "narrative": "Customer made 5 structured deposits of $9,900 each within 3-day period.",
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
    
    def store_risk_score_dynamodb(self, analysis_id: str, risk_data: Dict):
        """Store risk score in DynamoDB"""
        if not self.dynamodb:
            logger.warning("DynamoDB not available")
            return
        
        try:
            table_name = "aml-risk-scores"
            
            # Create table if it doesn't exist
            try:
                table = self.dynamodb.Table(table_name)
                table.load()
            except:
                table = self.dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'document_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'timestamp',
                            'KeyType': 'RANGE'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'document_id',
                            'AttributeType': 'S'
                        },
                        {
                            'AttributeName': 'timestamp',
                            'AttributeType': 'N'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                table.wait_until_exists()
                logger.info(f"Created DynamoDB table: {table_name}")
            
            # Store risk data (convert floats to Decimal for DynamoDB)
            from decimal import Decimal
            
            item = {
                'document_id': analysis_id,
                'timestamp': int(datetime.utcnow().timestamp()),
                'risk_score': Decimal(str(risk_data.get('final_risk_score', 0))),
                'risk_level': risk_data.get('risk_level', 'UNKNOWN'),
                'sanctions_risk': Decimal(str(risk_data.get('sanctions_risk', 0))),
                'pep_risk': Decimal(str(risk_data.get('pep_risk', 0))),
                'adverse_media_risk': Decimal(str(risk_data.get('adverse_media_risk', 0))),
                'flags': risk_data.get('flags', []),
                'recommendations': risk_data.get('recommendations', [])
            }
            
            table.put_item(Item=item)
            logger.info(f"✓ Stored risk score in DynamoDB: {analysis_id}")
            
        except Exception as e:
            logger.error(f"Failed to store risk score in DynamoDB: {e}")
    
    def send_to_processing_queue(self, message: Dict):
        """Send message to SQS processing queue"""
        if not self.sqs_client:
            logger.warning("SQS client not available")
            return
        
        try:
            queue_name = "aml-processing-queue"
            
            # Create queue if it doesn't exist
            try:
                response = self.sqs_client.get_queue_url(QueueName=queue_name)
                queue_url = response['QueueUrl']
            except:
                response = self.sqs_client.create_queue(
                    QueueName=queue_name,
                    Attributes={
                        'DelaySeconds': '0',
                        'MessageRetentionPeriod': '1209600'  # 14 days
                    }
                )
                queue_url = response['QueueUrl']
                logger.info(f"Created SQS queue: {queue_name}")
            
            # Send message
            self.sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message),
                MessageAttributes={
                    'analysis_id': {
                        'StringValue': message.get('analysis_id', ''),
                        'DataType': 'String'
                    },
                    'priority': {
                        'StringValue': message.get('priority', 'normal'),
                        'DataType': 'String'
                    }
                }
            )
            
            logger.info(f"✓ Sent message to processing queue: {message.get('analysis_id')}")
            
        except Exception as e:
            logger.error(f"Failed to send message to SQS: {e}")
    
    def setup_aws_resources(self):
        """Setup required AWS resources"""
        try:
            # Create S3 bucket
            if self.s3_client:
                try:
                    self.s3_client.head_bucket(Bucket=self.s3_bucket)
                    logger.info(f"✓ S3 bucket exists: {self.s3_bucket}")
                except:
                    # Create bucket with proper location constraint
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.s3_bucket)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.s3_bucket,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    logger.info(f"✓ Created S3 bucket: {self.s3_bucket}")
            
            # Create DynamoDB table
            if self.dynamodb:
                try:
                    table = self.dynamodb.Table("aml-risk-scores")
                    table.load()
                    logger.info("✓ DynamoDB table exists: aml-risk-scores")
                except:
                    table = self.dynamodb.create_table(
                        TableName="aml-risk-scores",
                        KeySchema=[
                            {'AttributeName': 'document_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                        ],
                        AttributeDefinitions=[
                            {'AttributeName': 'document_id', 'AttributeType': 'S'},
                            {'AttributeName': 'timestamp', 'AttributeType': 'N'}
                        ],
                        BillingMode='PAY_PER_REQUEST'
                    )
                    table.wait_until_exists()
                    logger.info("✓ Created DynamoDB table: aml-risk-scores")
            
            logger.info("✓ AWS resources setup complete")
            
        except Exception as e:
            logger.error(f"AWS resources setup failed: {e}")


# Global AWS service manager instance
aws_manager = AWSServiceManager()

# Setup AWS resources on import (if credentials available)
try:
    if aws_manager.s3_client:
        aws_manager.setup_aws_resources()
except Exception as e:
    logger.warning(f"AWS setup skipped: {e}")