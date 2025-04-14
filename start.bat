@echo off

echo Activating the virtual environment...
call .venv\Scripts\activate

echo Starting application...
call python automotive_ai/app.py

pause