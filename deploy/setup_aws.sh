#!/bin/bash

# AWS Setup Script for AML Intelligence System
set -e

echo "🚀 Setting up AWS resources for AML Intelligence System..."

# Configuration
REGION=${AWS_REGION:-us-east-1}
BUCKET_NAME="aml-documents-$(date +%s)"
TABLE_NAME="aml-risk-scores"
QUEUE_NAME="aml-processing-queue"

echo "📍 Region: $REGION"
echo "🪣 S3 Bucket: $BUCKET_NAME"

# Create S3 bucket for documents
echo "📦 Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION

# Set bucket policy for secure access
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AMLDocumentAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):root"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json
rm bucket-policy.json

# Create DynamoDB table for risk scores
echo "🗄️ Creating DynamoDB table..."
aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        AttributeName=document_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=N \
    --key-schema \
        AttributeName=document_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION

# Wait for table to be created
echo "⏳ Waiting for DynamoDB table to be ready..."
aws dynamodb wait table-exists --table-name $TABLE_NAME --region $REGION

# Create SQS queue for processing
echo "📬 Creating SQS queue..."
QUEUE_URL=$(aws sqs create-queue \
    --queue-name $QUEUE_NAME \
    --attributes DelaySeconds=0,MessageRetentionPeriod=1209600 \
    --region $REGION \
    --query 'QueueUrl' \
    --output text)

echo "📋 Queue URL: $QUEUE_URL"

# Enable Bedrock models
echo "🤖 Enabling Bedrock models..."
aws bedrock put-model-invocation-logging-configuration \
    --logging-config cloudWatchConfig='{logGroupName="/aws/bedrock/modelinvocations",roleArn="arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/service-role/AmazonBedrockExecutionRoleForCloudWatchLogs"}' \
    --region $REGION || echo "⚠️ Bedrock logging setup failed (may not be available in region)"

# Create IAM role for Lambda
echo "🔐 Creating IAM role for Lambda..."
cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

aws iam create-role \
    --role-name AMLIntelligenceSystemRole \
    --assume-role-policy-document file://trust-policy.json || echo "Role may already exist"

# Attach policies
aws iam attach-role-policy \
    --role-name AMLIntelligenceSystemRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

cat > lambda-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": "arn:aws:dynamodb:$REGION:$(aws sts get-caller-identity --query Account --output text):table/$TABLE_NAME"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sqs:SendMessage",
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage"
            ],
            "Resource": "arn:aws:sqs:$REGION:$(aws sts get-caller-identity --query Account --output text):$QUEUE_NAME"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name AMLIntelligenceSystemRole \
    --policy-name AMLIntelligenceSystemPolicy \
    --policy-document file://lambda-policy.json

# Clean up temporary files
rm trust-policy.json lambda-policy.json

# Output environment variables
echo ""
echo "✅ AWS resources created successfully!"
echo ""
echo "📝 Add these to your .env file:"
echo "AWS_REGION=$REGION"
echo "S3_BUCKET_NAME=$BUCKET_NAME"
echo "DYNAMODB_TABLE_NAME=$TABLE_NAME"
echo "SQS_QUEUE_URL=$QUEUE_URL"
echo ""
echo "🚀 Ready to deploy the AML Intelligence System!"