"""
MindMirror AI - Hugging Face Spaces Deployment
This is the entry point for Hugging Face Spaces deployment.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Flask API server
from api_server import app

if __name__ == "__main__":
    # Get port from environment (HF Spaces uses 7860)
    port = int(os.getenv("PORT", 7860))
    
    print(f"🚀 Starting MindMirror AI on Hugging Face Spaces")
    print(f"📍 Port: {port}")
    
    # Run the Flask app
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
