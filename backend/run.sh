#!/bin/bash
# Start the STEALTH Bot backend

echo "Starting STEALTH Bot Backend..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the API server
echo "Starting API server..."
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000