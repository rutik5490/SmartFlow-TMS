@echo off
echo ========================================
echo SmartFlow TMS - Startup Script
echo ========================================
echo.

echo [1/4] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)
echo Docker found.
echo.

echo [2/4] Building and starting services...
docker-compose up -d
echo.

echo [3/4] Waiting for services to start (30 seconds)...
timeout /t 30 /nobreak
echo.

echo [4/4] Checking service status...
docker-compose ps
echo.

echo ========================================
echo Services Started Successfully!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo API Docs:    http://localhost:8000/docs
echo Spark UI:    http://localhost:8080
echo.
echo Frontend: Open traffic_management_system.html in your browser
echo.
echo To view logs: docker-compose logs -f
echo To stop:      docker-compose down
echo.
pause
