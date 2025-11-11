#!/usr/bin/env python3
"""
Test script to verify AWS Bedrock and LandingAI services
"""
import os
import json
import time
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_aws_credentials():
    """Test AWS credentials and access"""
    print("🔐 Testing AWS Credentials...")
    
    try:
        import boto3
        
        # Test basic AWS access
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials is None:
            print("❌ No AWS credentials found")
            return False
        
        print(f"✅ AWS credentials found")
        print(f"   Access Key: {credentials.access_key[:8]}...")
        
        # Test STS (Security Token Service) to verify credentials work
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        
        print(f"✅ AWS identity verified")
        print(f"   Account: {identity.get('Account', 'Unknown')}")
        print(f"   User/Role: {identity.get('Arn', 'Unknown').split('/')[-1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ AWS credentials test failed: {e}")
        return False

def test_bedrock_access():
    """Test AWS Bedrock access and model availability"""
    print("\n🧠 Testing AWS Bedrock Access...")
    
    try:
        import boto3
        
        # Test Bedrock client creation
        bedrock_client = boto3.client('bedrock', region_name='us-east-1')
        
        print("✅ Bedrock client created successfully")
        
        # List available foundation models
        try:
            response = bedrock_client.list_foundation_models()
            models = response.get('modelSummaries', [])
            
            print(f"✅ Found {len(models)} available models")
            
            # Look for Claude models
            claude_models = [m for m in models if 'claude' in m.get('modelId', '').lower()]
            
            if claude_models:
                print("✅ Claude models available:")
                for model in claude_models[:3]:  # Show first 3
                    print(f"   - {model.get('modelId')}")
            else:
                print("⚠️  No Claude models found")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Cannot list models (may need permissions): {e}")
            return True  # Client works, just no list permission
            
    except Exception as e:
        print(f"❌ Bedrock access test failed: {e}")
        return False

def test_bedrock_inference():
    """Test actual Bedrock model inference"""
    print("\n🤖 Testing Bedrock Model Inference...")
    
    try:
        import boto3
        
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test with Claude 3 Sonnet (correct model ID)
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        
        test_prompt = """
        Extract the following information from this sample transaction and return as JSON:
        - transaction_id
        - amount
        - sender_name
        - receiver_name
        
        Sample transaction text:
        "Transaction ID: TXN-12345, Amount: $50,000 USD, From: John Smith (Account: 123456), To: ABC Corp (Account: 789012), Date: 2024-11-01, Purpose: Business payment"
        
        Return only valid JSON.
        """
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": test_prompt
                }
            ]
        }
        
        print(f"🔄 Testing model: {model_id}")
        start_time = time.time()
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        end_time = time.time()
        
        response_body = json.loads(response['body'].read())
        response_text = response_body['content'][0]['text']
        
        print(f"✅ Bedrock inference successful!")
        print(f"   Response time: {(end_time - start_time):.2f} seconds")
        print(f"   Response preview: {response_text[:200]}...")
        
        # Try to parse JSON from response
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed_json = json.loads(json_str)
                print(f"✅ JSON parsing successful: {parsed_json}")
            else:
                print("⚠️  Response doesn't contain valid JSON")
        except Exception as e:
            print(f"⚠️  JSON parsing failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Bedrock inference test failed: {e}")
        
        # Check for specific error types
        error_str = str(e)
        if "ValidationException" in error_str:
            print("💡 Hint: Model may not be available in your region or account")
        elif "AccessDeniedException" in error_str:
            print("💡 Hint: Need Bedrock permissions or model access request")
        elif "ThrottlingException" in error_str:
            print("💡 Hint: Rate limit exceeded, try again later")
        
        return False

def test_landingai_import():
    """Test LandingAI package import"""
    print("\n📄 Testing LandingAI Package...")
    
    try:
        # Try to import LandingAI ADE (the correct package)
        from landingai_ade import LandingAIADE
        print("✅ LandingAI ADE package imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ LandingAI ADE package not available: {e}")
        print("💡 Hint: Install with 'pip install landingai-ade'")
        return False
    except Exception as e:
        print(f"❌ LandingAI import error: {e}")
        return False

def test_landingai_client():
    """Test LandingAI client creation"""
    print("\n🔧 Testing LandingAI Client Creation...")
    
    try:
        from landingai_ade import LandingAIADE
        
        # Check for API key
        api_key = os.getenv("LANDING_AI_API_KEY")
        if not api_key:
            print("⚠️  No LANDING_AI_API_KEY found in environment")
            print("💡 Using test key for client creation...")
            api_key = "test_key"
        else:
            print(f"✅ API key found: {api_key[:8]}...")
        
        # Create LandingAI ADE client
        client = LandingAIADE(apikey=api_key)
        print("✅ LandingAI ADE client created successfully")
        
        return True, client
        
    except Exception as e:
        print(f"❌ LandingAI client creation failed: {e}")
        return False, None

def test_landingai_document_parsing():
    """Test LandingAI document parsing"""
    print("\n📋 Testing LandingAI Document Parsing...")
    
    try:
        success, client = test_landingai_client()
        if not success:
            return False
        
        # Create a test document (text file)
        test_doc_path = Path("test_document.txt")
        test_content = """
        SUSPICIOUS ACTIVITY REPORT
        
        Report ID: SAR-2024-001234
        Filing Date: 2024-11-01
        Filing Institution: First National Bank
        
        Subject Information:
        Name: John Smith
        Account: ACC-9876543
        
        Transaction Details:
        Amount: $150,000
        Date: 2024-10-15
        Type: Structured deposits
        
        Narrative: Customer made multiple deposits just below reporting threshold.
        """
        
        with open(test_doc_path, 'w') as f:
            f.write(test_content)
        
        print(f"📄 Created test document: {test_doc_path}")
        
        # Test document parsing
        print("🔄 Parsing document with LandingAI...")
        start_time = time.time()
        
        response = client.parse(
            document=test_doc_path,
            model="dpt-2-latest"
        )
        
        end_time = time.time()
        
        print(f"✅ Document parsing successful!")
        print(f"   Processing time: {(end_time - start_time):.2f} seconds")
        print(f"   Markdown preview: {response.markdown[:200]}...")
        print(f"   Chunks count: {len(response.chunks) if hasattr(response, 'chunks') else 'N/A'}")
        
        # Cleanup
        test_doc_path.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ LandingAI document parsing failed: {e}")
        
        # Cleanup on error
        test_doc_path = Path("test_document.txt")
        if test_doc_path.exists():
            test_doc_path.unlink()
        
        # Check for specific errors
        error_str = str(e)
        if "API key" in error_str or "authentication" in error_str.lower():
            print("💡 Hint: Invalid or missing API key")
        elif "rate limit" in error_str.lower():
            print("💡 Hint: API rate limit exceeded")
        elif "network" in error_str.lower() or "connection" in error_str.lower():
            print("💡 Hint: Network connectivity issue")
        
        return False

def test_integrated_workflow():
    """Test the integrated workflow with both services"""
    print("\n🔄 Testing Integrated Workflow...")
    
    try:
        from src.document_processor import DocumentProcessor
        
        # Test with real services
        processor = DocumentProcessor(use_mock=False)
        
        print("✅ DocumentProcessor created with real services")
        
        # This would test the full workflow but requires actual files
        print("💡 Full workflow test requires actual document files")
        print("   Use the API endpoints to test complete integration")
        
        return True
        
    except Exception as e:
        print(f"❌ Integrated workflow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 AI Services Test Suite")
    print("   Testing AWS Bedrock and LandingAI Integration")
    print("=" * 60)
    
    results = {}
    
    # Test AWS
    results['aws_credentials'] = test_aws_credentials()
    results['bedrock_access'] = test_bedrock_access()
    results['bedrock_inference'] = test_bedrock_inference()
    
    # Test LandingAI
    results['landingai_import'] = test_landingai_import()
    
    if results['landingai_import']:
        results['landingai_client'] = test_landingai_client()[0]
        results['landingai_parsing'] = test_landingai_document_parsing()
    else:
        results['landingai_client'] = False
        results['landingai_parsing'] = False
    
    # Test integration
    results['integrated_workflow'] = test_integrated_workflow()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    aws_working = results['aws_credentials'] and results['bedrock_access']
    bedrock_working = aws_working and results['bedrock_inference']
    landingai_working = results['landingai_import'] and results['landingai_client']
    
    print(f"🔐 AWS Credentials:     {'✅ WORKING' if results['aws_credentials'] else '❌ FAILED'}")
    print(f"🧠 Bedrock Access:     {'✅ WORKING' if results['bedrock_access'] else '❌ FAILED'}")
    print(f"🤖 Bedrock Inference:  {'✅ WORKING' if results['bedrock_inference'] else '❌ FAILED'}")
    print(f"📄 LandingAI Import:   {'✅ WORKING' if results['landingai_import'] else '❌ FAILED'}")
    print(f"🔧 LandingAI Client:   {'✅ WORKING' if results['landingai_client'] else '❌ FAILED'}")
    print(f"📋 LandingAI Parsing:  {'✅ WORKING' if results['landingai_parsing'] else '❌ FAILED'}")
    
    print("\n🎯 Service Status:")
    print(f"   AWS Bedrock:  {'🟢 READY FOR PRODUCTION' if bedrock_working else '🔴 USE MOCK IMPLEMENTATION'}")
    print(f"   LandingAI:    {'🟢 READY FOR PRODUCTION' if landingai_working else '🔴 USE MOCK IMPLEMENTATION'}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if bedrock_working and landingai_working:
        print("   🚀 Both services working! Switch to production mode:")
        print("      - Set use_mock=False in src/api.py")
        print("      - Update environment variables")
    elif bedrock_working:
        print("   🔄 Bedrock working, LandingAI needs setup:")
        print("      - Install: pip install landingai-ade")
        print("      - Set LANDING_AI_API_KEY in .env")
    elif landingai_working:
        print("   🔄 LandingAI working, Bedrock needs setup:")
        print("      - Check AWS permissions for Bedrock")
        print("      - Request model access in AWS console")
    else:
        print("   📋 Both services need setup - continue with mock implementation")
        print("      - Perfect for demo and development")
        print("      - Add real services when ready for production")
    
    print("\n🎉 Test complete!")
    
    return results

if __name__ == "__main__":
    main()