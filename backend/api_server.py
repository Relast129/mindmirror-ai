"""
Simple Flask API Server for MindMirror AI
Wraps the Gradio backend functions with REST API endpoints
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the API functions from app.py
from app import api_login, api_submit, api_history, api_download, api_feedback

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Helper to run async functions in Flask
def run_async(coro):
    """Run async function in Flask route"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    """Handle OAuth login"""
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json() or {}
    code = data.get('code')
    result = api_login(code)
    return jsonify(result)

@app.route('/api/submit', methods=['POST', 'OPTIONS'])
def submit():
    """Handle journal submission"""
    if request.method == 'OPTIONS':
        return '', 200
    
    # Get form data or JSON
    if request.is_json:
        data = request.get_json()
        session_token = data.get('session_token')
        input_type = data.get('input_type', 'text')
        text_content = data.get('text_content', '')
        file_data = None
    else:
        session_token = request.form.get('session_token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        input_type = request.form.get('input_type', 'text')
        text_content = request.form.get('text_content', '')
        file_data = request.files.get('file_data')
    
    result = run_async(api_submit(session_token, input_type, text_content, file_data))
    return jsonify(result)

@app.route('/api/history', methods=['GET', 'OPTIONS'])
def history():
    """Get entry history"""
    if request.method == 'OPTIONS':
        return '', 200
    
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    limit = int(request.args.get('limit', 50))
    
    result = api_history(session_token, limit)
    return jsonify(result)

@app.route('/api/download', methods=['GET', 'OPTIONS'])
def download():
    """Download file"""
    if request.method == 'OPTIONS':
        return '', 200
    
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    file_id = request.args.get('file_id', '')
    
    result = api_download(session_token, file_id)
    return jsonify(result)

@app.route('/api/feedback', methods=['POST', 'OPTIONS'])
def feedback():
    """Add feedback"""
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json() or {}
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    entry_id = data.get('entry_id', '')
    feedback_text = data.get('feedback', '')
    
    result = api_feedback(session_token, entry_id, feedback_text)
    return jsonify(result)

@app.route('/callback', methods=['GET'])
def callback():
    """Handle OAuth callback from Google"""
    code = request.args.get('code')
    if code:
        # Exchange code for tokens
        result = api_login(code)
        
        if result.get('session_token'):
            # Redirect to frontend with session token
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            redirect_url = f"{frontend_url}/callback?session_token={result['session_token']}"
            return f"""
            <html>
                <head>
                    <title>Redirecting...</title>
                    <script>
                        window.location.href = "{redirect_url}";
                    </script>
                </head>
                <body>
                    <p>Redirecting to app...</p>
                </body>
            </html>
            """
        else:
            return jsonify({"error": "Login failed"}), 400
    else:
        return jsonify({"error": "No code provided"}), 400

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "healthy", "service": "MindMirror AI API"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 7860))
    print(f"🚀 Starting MindMirror AI API Server on port {port}")
    print(f"📍 API endpoints available at http://localhost:{port}/api/")
    app.run(host='0.0.0.0', port=port, debug=False)
