#!/bin/bash

conda create -n auto-ai python=3.12 -y

echo "Installing Python requirements..."
pip install -r src/requirements.txt

echo "Downloading SpaCy model..."
python -m spacy download en_core_web_md

echo "Installation completed."
