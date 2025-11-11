"""
Configuration for VORTEX-AML System
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # AWS Configuration
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # Check if AWS credentials are real (not placeholders)
    AWS_CREDENTIALS_VALID = (
        AWS_ACCESS_KEY_ID and 
        AWS_SECRET_ACCESS_KEY and
        not AWS_ACCESS_KEY_ID.startswith("your_") and
        not AWS_SECRET_ACCESS_KEY.startswith("your_")
    )
    
    # LandingAI Configuration
    LANDING_AI_API_KEY = os.getenv("LANDING_AI_API_KEY") or os.getenv("VISION_AGENT_API_KEY")
    LANDING_AI_AVAILABLE = bool(LANDING_AI_API_KEY and not LANDING_AI_API_KEY.startswith("your_"))
    
    # Service Mode Configuration
    # AUTO mode: Use real services if available, fallback to mock
    # REAL mode: Force real services (will fail if not available)
    # MOCK mode: Force mock services for demo
    SERVICE_MODE = os.getenv("SERVICE_MODE", "AUTO").upper()
    
    # Determine which services to use based on availability
    if SERVICE_MODE == "MOCK":
        USE_REAL_LANDINGAI = False
        USE_REAL_BEDROCK = False
    elif SERVICE_MODE == "REAL":
        USE_REAL_LANDINGAI = True
        USE_REAL_BEDROCK = True
    else:  # AUTO mode
        USE_REAL_LANDINGAI = LANDING_AI_AVAILABLE
        USE_REAL_BEDROCK = AWS_CREDENTIALS_VALID
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aml_system.db")
    
    # Application
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    @classmethod
    def get_service_status(cls):
        """Get current service configuration status"""
        return {
            "mode": cls.SERVICE_MODE,
            "landingai": {
                "available": cls.LANDING_AI_AVAILABLE,
                "using": cls.USE_REAL_LANDINGAI,
                "status": "✅ REAL" if cls.USE_REAL_LANDINGAI else "📝 MOCK"
            },
            "bedrock": {
                "available": cls.AWS_CREDENTIALS_VALID,
                "using": cls.USE_REAL_BEDROCK,
                "status": "✅ REAL" if cls.USE_REAL_BEDROCK else "📝 MOCK"
            }
        }
    
    @classmethod
    def print_status(cls):
        """Print service configuration status"""
        status = cls.get_service_status()
        
        print("=" * 70)
        print("VORTEX-AML Service Configuration")
        print("=" * 70)
        print(f"Mode: {status['mode']}")
        print()
        print(f"LandingAI ADE: {status['landingai']['status']}")
        print(f"  Available: {status['landingai']['available']}")
        print(f"  Using: {'Real Service' if status['landingai']['using'] else 'Mock Implementation'}")
        print()
        print(f"AWS Bedrock LLM: {status['bedrock']['status']}")
        print(f"  Available: {status['bedrock']['available']}")
        print(f"  Using: {'Real Service' if status['bedrock']['using'] else 'Mock Implementation'}")
        print()
        
        if not status['landingai']['available'] and not status['bedrock']['available']:
            print("⚠️  No real AI services available - using full mock mode")
            print("   System will work with demo data for presentation")
        elif status['landingai']['available'] and not status['bedrock']['available']:
            print("✅ LandingAI available - Document processing will use real AI")
            print("⚠️  Bedrock not available - Risk analysis will use mock LLM")
        elif not status['landingai']['available'] and status['bedrock']['available']:
            print("⚠️  LandingAI not available - Document processing will use mock")
            print("✅ Bedrock available - Risk analysis will use real LLM")
        else:
            print("🎉 All AI services available - Full real-time AI processing!")
        
        print("=" * 70)


# Create global config instance
config = Config()

if __name__ == "__main__":
    config.print_status()
