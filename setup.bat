@echo off
REM Setup script for Django Expense Tracker (Windows)
REM Run this script to complete the setup

echo ==========================================
echo Django Expense Tracker - Setup Script
echo ==========================================

REM Step 1: Create .env file
echo.
echo Step 1: Creating .env file...
if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file from .env.example
    echo ⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY!
    echo    Get your API key from: https://aistudio.google.com/app/apikey
) else (
    echo ℹ️  .env file already exists
)

REM Step 2: Create superuser
echo.
echo Step 2: Creating superuser account...
echo Please enter your desired admin credentials:
C:\Users\Kavin\Documents\expense_tracker\.venv\Scripts\python.exe manage.py createsuperuser

REM Step 3: Create demo data (optional)
echo.
set /p create_demo="Step 3: Would you like to create demo data? (y/n): "
if /i "%create_demo%"=="y" (
    echo Creating demo data...
    C:\Users\Kavin\Documents\expense_tracker\.venv\Scripts\python.exe manage.py shell < create_demo_data.py
    echo ✅ Demo data created!
)

REM Step 4: Final instructions
echo.
echo ==========================================
echo ✅ Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env and add your GEMINI_API_KEY
echo 2. Run the server:
echo    C:\Users\Kavin\Documents\expense_tracker\.venv\Scripts\python.exe manage.py runserver
echo.
echo 3. Visit: http://127.0.0.1:8000
echo.
echo Happy expense tracking! 💰
echo ==========================================
pause
