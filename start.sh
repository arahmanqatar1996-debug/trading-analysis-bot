#!/bin/bash
# Render.com deployment script
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting bot..."
python main.py
