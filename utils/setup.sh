#!/bin/bash

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt

# Generate secret key
python utils/flask_keygen.py

# Initialize git hooks
cp utils/pre-push .git/hooks/
chmod +x .git/hooks/pre-push

echo "Setup complete! Don't forget to:"
echo "1. Create a .env file with your configuration"
echo "2. Update the app name in src/app_name"
echo "3. Configure your Fly.io deployment settings"
