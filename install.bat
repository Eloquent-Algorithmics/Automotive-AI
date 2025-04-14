@echo off

echo Creating a new virtual environment...
call python -m venv .venv

echo Activating the virtual environment...
call .venv\Scripts\activate

echo Installing the Python requirements...
call pip install -r requirements-dev.txt

echo Installation completed.

echo Starting application...
call python automotive_ai/app.py

pause