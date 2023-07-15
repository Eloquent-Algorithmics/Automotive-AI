#!/bin/bash

echo "Installing Python requirements..."
pip install -r requirements.txt

echo "Downloading SpaCy model..."
python -m spacy download en_core_web_lg

echo "Cloning J2534_cffi repository..."
git clone https://github.com/MCU-Innovations/J2534_cffi.git

echo "Installing J2534_cffi..."
cd J2534_cffi
pip install .

echo "Returning to the original directory..."
cd ..

echo "Installation completed."