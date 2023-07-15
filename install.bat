@echo off

echo Installing Python requirements...
pip install -r requirements.txt

echo Downloading SpaCy model...
python -m spacy download en_core_web_lg

echo Installation completed.
pause