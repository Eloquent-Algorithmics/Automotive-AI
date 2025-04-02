#!/bin/bash

conda create -n auto_ai python=3.12 -y

echo "Installing Python requirements..."
pip install -r requirements-dev.txt

echo "Downloading SpaCy model..."
python -m spacy download en_core_web_md

echo "Installation completed."

echo "To continue, please activate the conda environment with the following command:"
echo "conda activate auto_ai"

echo "Then, run the following command to start the application:"
echo "python automotive_ai/app.py"
