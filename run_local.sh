#!/bin/bash
# MindMirror AI - Local Development Script

echo "🧠 Starting MindMirror AI Backend (Gradio)..."

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env with your credentials before continuing."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "backend/venv" ]; then
    echo "🔧 Activating virtual environment..."
    source backend/venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
cd backend
pip install -r requirements.txt

# Run the Gradio app
echo "🚀 Launching Gradio backend on http://localhost:7860"
echo "📡 API will be available at http://localhost:7860/api/"
echo "Press Ctrl+C to stop"
echo ""

python app.py
