"""
MindMirror AI - Hugging Face Spaces Deployment
This is the entry point for Hugging Face Spaces deployment.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔧 Importing Flask API server...")
try:
    from api_server import app
    print("✅ Flask app imported successfully")
except Exception as e:
    print(f"❌ Error importing Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    # Get port from environment (HF Spaces uses 7860)
    port = int(os.getenv("PORT", 7860))
    
    print(f"🚀 Starting MindMirror AI on Hugging Face Spaces")
    print(f"📍 Port: {port}")
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"📁 Files in directory: {os.listdir('.')}")
    
    # Check environment variables
    if os.getenv("OPENROUTER_API_KEY"):
        print("✅ OpenRouter API key configured")
    else:
        print("⚠️  OpenRouter API key not set - will use fallbacks")
    
    if os.getenv("GOOGLE_CLIENT_ID"):
        print("✅ Google OAuth configured")
    else:
        print("❌ Google OAuth not configured")
    
    # Run the Flask app
    try:
        app.run(
            host="0.0.0.0",
            port=port,
            debug=False
        )
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
