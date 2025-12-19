#!/bin/bash
# Local test script for Pharmyrus V5.0

echo "🧪 Pharmyrus V5.0 - Local Test"
echo "=============================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Set test PORT
export PORT=8000
export LOG_LEVEL=info

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting Pharmyrus V5.0..."
echo "   URL: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   Health: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start server
cd app && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
