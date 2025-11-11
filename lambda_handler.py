"""
AWS Lambda handler for AML Intelligence System
"""
import os
import sys

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mangum import Mangum
from src.api import app

# Create Lambda handler
lambda_handler = Mangum(app, lifespan="off")

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)