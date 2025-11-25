#!/bin/bash
# Quick Start Script for URL Guardian Backend

echo "🚀 URL Guardian Backend - Quick Start"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python --version)"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")" || exit 1
echo "📁 Current directory: $(pwd)"
echo ""

# Create virtual environment (optional but recommended)
echo "🔧 Setting up environment..."
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    echo "  ✅ Virtual environment created"
else
    echo "  ✅ Virtual environment already exists"
    source venv/bin/activate
fi

echo ""
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "  1. Start the server:  python main.py"
echo "  2. API docs:          http://localhost:8000/docs"
echo "  3. Test endpoint:     curl -X POST http://localhost:8000/api/check_url_fast -H 'Content-Type: application/json' -d '{\"url\": \"https://example.com\"}'"
echo ""
