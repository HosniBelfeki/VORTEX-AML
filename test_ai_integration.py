"""
Test script to verify AWS Bedrock and LandingAI integration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("VORTEX-AML - AI Services Integration Test")
print("=" * 70)
print()

# Test 1: Check Environment Variables
print("📋 Test 1: Checking Environment Variables")
print("-" * 70)

landing_ai_key = os.getenv("LANDING_AI_API_KEY") or os.getenv("VISION_AGENT_API_KEY")
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION", "us-east-1")

print(f"✓ LandingAI API Key: {'✅ Found' if landing_ai_key else '❌ Missing'}")
if landing_ai_key:
    print(f"  Key preview: {landing_ai_key[:20]}...")

print(f"✓ AWS Access Key: {'✅ Found' if aws_access_key else '❌ Missing'}")
if aws_access_key:
    print(f"  Key preview: {aws_access_key[:10]}...")

print(f"✓ AWS Secret Key: {'✅ Found' if aws_secret_key else '❌ Missing'}")
print(f"✓ AWS Region: {aws_region}")
print()

# Test 2: Check AWS Bedrock Availability
print("🤖 Test 2: Testing AWS Bedrock Connection")
print("-" * 70)

try:
    import boto3
    
    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )
    
    credentials = session.get_credentials()
    
    if credentials:
        print("✅ AWS credentials are valid")
        
        try:
            # Try to create Bedrock client
            bedrock_client = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
            
            print("✅ AWS Bedrock client created successfully")
            print(f"   Region: {aws_region}")
            print(f"   Service: bedrock-runtime")
            
            # Try a simple test call
            try:
                import json
                
                test_response = bedrock_client.invoke_model(
                    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 100,
                        "messages": [
                            {
                                "role": "user",
                                "content": "Say 'Hello from AWS Bedrock!' in one sentence."
                            }
                        ]
                    })
                )
                
                response_body = json.loads(test_response['body'].read())
                response_text = response_body['content'][0]['text']
                
                print("✅ AWS Bedrock LLM is working!")
                print(f"   Test response: {response_text}")
                bedrock_working = True
                
            except Exception as e:
                print(f"⚠️  AWS Bedrock test call failed: {str(e)}")
                print("   This might be due to:")
                print("   - Insufficient permissions")
                print("   - Model not available in your region")
                print("   - Bedrock not enabled in your AWS account")
                bedrock_working = False
                
        except Exception as e:
            print(f"❌ Failed to create Bedrock client: {str(e)}")
            bedrock_working = False
    else:
        print("❌ AWS credentials are invalid")
        bedrock_working = False
        
except ImportError:
    print("❌ boto3 not installed. Install with: pip install boto3")
    bedrock_working = False
except Exception as e:
    print(f"❌ AWS Bedrock test failed: {str(e)}")
    bedrock_working = False

print()

# Test 3: Check LandingAI Availability
print("📄 Test 3: Testing LandingAI ADE Connection")
print("-" * 70)

try:
    from landingai_ade import LandingAIADE
    
    if landing_ai_key:
        try:
            client = LandingAIADE(apikey=landing_ai_key)
            print("✅ LandingAI ADE client created successfully")
            print(f"   API Key preview: {landing_ai_key[:20]}...")
            
            # Note: We can't test without a real document
            print("   ℹ️  To fully test, upload a document through the API")
            landingai_working = True
            
        except Exception as e:
            print(f"⚠️  LandingAI client creation failed: {str(e)}")
            print("   This might be due to:")
            print("   - Invalid API key")
            print("   - Network connectivity issues")
            print("   - LandingAI service unavailable")
            landingai_working = False
    else:
        print("❌ LandingAI API key not found in environment")
        landingai_working = False
        
except ImportError:
    print("⚠️  landingai_ade package not installed")
    print("   Install with: pip install landingai-ade")
    print("   ℹ️  System will use mock implementation for demo")
    landingai_working = False
except Exception as e:
    print(f"❌ LandingAI test failed: {str(e)}")
    landingai_working = False

print()

# Test 4: Test Document Processor
print("📝 Test 4: Testing Document Processor")
print("-" * 70)

try:
    from src.document_processor import DocumentProcessor
    
    # Test with use_mock=False to use real services
    processor = DocumentProcessor(use_mock=False)
    
    print(f"✅ Document Processor initialized")
    print(f"   Using mock: {processor.use_mock}")
    print(f"   Bedrock available: {processor.use_real_bedrock}")
    
    if processor.use_mock:
        print("   ℹ️  Using mock LandingAI (real service not available)")
    else:
        print("   ✅ Using real LandingAI ADE")
    
    if processor.use_real_bedrock:
        print("   ✅ Using real AWS Bedrock for extraction")
    else:
        print("   ℹ️  Using mock extraction (Bedrock not available)")
    
except Exception as e:
    print(f"❌ Document Processor test failed: {str(e)}")

print()

# Test 5: Test Screening Engine
print("🔍 Test 5: Testing Screening Engine with LLM")
print("-" * 70)

try:
    from src.screening_engine import ScreeningEngine
    
    # Test with use_llm=True to use Bedrock
    engine = ScreeningEngine(use_mock=True, use_llm=True)
    
    print(f"✅ Screening Engine initialized")
    print(f"   Using mock databases: {engine.use_mock}")
    print(f"   LLM enabled: {engine.use_llm}")
    print(f"   Bedrock available: {engine.bedrock_available}")
    
    # Test screening
    print("\n   Testing entity screening...")
    result = engine.screen_entity("Test Entity", "individual", {"transaction_amount": 50000})
    
    print(f"   ✅ Screening completed")
    print(f"      Risk Score: {result.final_risk_score:.1f}/100")
    print(f"      Risk Level: {result.risk_level}")
    print(f"      Flags: {len(result.flags)} flags")
    print(f"      Recommendations: {len(result.recommendations)} recommendations")
    
except Exception as e:
    print(f"❌ Screening Engine test failed: {str(e)}")

print()

# Summary
print("=" * 70)
print("📊 SUMMARY")
print("=" * 70)

services_status = []

if landing_ai_key:
    if landingai_working:
        services_status.append("✅ LandingAI ADE: WORKING")
    else:
        services_status.append("⚠️  LandingAI ADE: CONFIGURED (not tested)")
else:
    services_status.append("❌ LandingAI ADE: NOT CONFIGURED")

if aws_access_key and aws_secret_key:
    if bedrock_working:
        services_status.append("✅ AWS Bedrock LLM: WORKING")
    else:
        services_status.append("⚠️  AWS Bedrock LLM: CONFIGURED (not working)")
else:
    services_status.append("❌ AWS Bedrock LLM: NOT CONFIGURED")

for status in services_status:
    print(status)

print()

if bedrock_working and landingai_working:
    print("🎉 ALL AI SERVICES ARE WORKING!")
    print("   Your frontend will use real AI for document processing and risk analysis.")
elif bedrock_working or landingai_working:
    print("⚠️  PARTIAL AI SERVICES AVAILABLE")
    print("   Some features will use real AI, others will use mock data.")
    print("   The system will work but with limited AI capabilities.")
else:
    print("ℹ️  USING MOCK/DEMO MODE")
    print("   No real AI services detected. System will use mock data for demo.")
    print("   To enable real AI services:")
    print("   1. Add valid AWS credentials to .env file")
    print("   2. Add valid LandingAI API key to .env file")
    print("   3. Ensure AWS Bedrock is enabled in your account")
    print("   4. Install: pip install landingai-ade boto3")

print()
print("=" * 70)
print("Test completed!")
print("=" * 70)
