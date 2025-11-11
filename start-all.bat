@echo off
echo ========================================
echo VORTEX-AML - Starting Backend and Frontend
echo ========================================
echo.

echo Checking AI Services Status...
python check_services.py
echo.

echo Starting Backend (FastAPI)...
start "VORTEX-AML Backend" cmd /k "python run.py"

timeout /t 5 /nobreak > nul

echo Starting Frontend (React + Vite)...
start "VORTEX-AML Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo VORTEX-AML is starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo AI Services Status:
echo - LandingAI: Check terminal for status
echo - AWS Bedrock: Check terminal for status
echo.
echo Press any key to exit...
pause > nul
