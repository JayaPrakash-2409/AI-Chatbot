#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo ""
echo "Starting NeuralChat..."
echo "Visit: http://localhost:5000"
echo ""
python app.py
