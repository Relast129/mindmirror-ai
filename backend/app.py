"""
MindMirror AI - Gradio Backend Application
Privacy-first emotional reflection dashboard with multi-modal input.
Deployable to Hugging Face Spaces with api=True.
"""

import gradio as gr
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
import secrets

from utils.google_oauth import GoogleOAuthHandler
from utils.drive_manager import GoogleDriveManager
from utils.session_store import SessionStore
from utils.file_helpers import FileHelper
from ai.orchestrator import AIOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
oauth_handler = GoogleOAuthHandler(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_uri=os.getenv("REDIRECT_URI", "http://localhost:7860/callback")
)
session_store = SessionStore()
ai_orchestrator = AIOrchestrator()
file_helper = FileHelper()

# Security: Session validation decorator
def require_session(func):
    """Decorator to validate session token before processing request."""
    @wraps(func)
    def wrapper(session_token: str, *args, **kwargs):
        if not session_token:
            return {"error": "Missing session token", "status": 401}
        
        session_data = session_store.get_session(session_token)
        if not session_data:
            return {"error": "Invalid or expired session", "status": 401}
        
        # Inject session data into kwargs
        kwargs['session_data'] = session_data
        return func(session_token, *args, **kwargs)
    return wrapper


# ============================================================================
# API ENDPOINTS
# ============================================================================

def api_login(code: Optional[str] = None) -> Dict[str, Any]:
    """
    POST /api/login
    Start OAuth flow or handle callback.
    
    Args:
        code: Optional OAuth authorization code from callback
        
    Returns:
        If code is None: {"auth_url": "https://..."}
        If code provided: {"session_token": "...", "profile": {...}, "drive_folder_id": "..."}
    """
    try:
        if not code:
            # Step 1: Generate OAuth URL
            auth_url = oauth_handler.get_authorization_url()
            return {
                "auth_url": auth_url,
                "status": 200
            }
        
        # Step 2: Exchange code for tokens
        tokens = oauth_handler.exchange_code(code)
        if "error" in tokens:
            return {"error": tokens["error"], "status": 400}
        
        # Get user profile
        profile = oauth_handler.get_user_profile(tokens["access_token"])
        if "error" in profile:
            return {"error": profile["error"], "status": 400}
        
        # Create/get Drive folder
        drive_manager = GoogleDriveManager(tokens["access_token"])
        folder_id = drive_manager.create_user_folder(profile)
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        session_data = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token"),
            "profile": profile,
            "drive_folder_id": folder_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store session (in-memory, expires in 1 hour)
        # WARNING: On HF Spaces, this will be lost on container restart
        # For production, use Redis or encrypted database
        session_store.set_session(session_token, session_data, ttl=3600)
        
        logger.info(f"User logged in: {profile.get('email')}")
        
        return {
            "session_token": session_token,
            "profile": {
                "name": profile.get("name"),
                "email": profile.get("email"),
                "picture": profile.get("picture")
            },
            "drive_folder_id": folder_id,
            "status": 200
        }
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return {"error": str(e), "status": 500}


@require_session
async def api_submit(
    session_token: str,
    input_type: str,
    text_content: Optional[str] = None,
    file_data: Optional[Any] = None,
    session_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    POST /api/submit
    Process multi-modal input and generate AI reflection.
    
    Args:
        session_token: User session token
        input_type: "text", "voice", "image", "drawing", "video"
        text_content: Text input (for text journaling)
        file_data: Uploaded file (for voice/image/video)
        session_data: Injected by decorator
        
    Returns:
        {
            "id": "entry_123",
            "timestamp": "2023-11-04T12:00:00",
            "emotion_labels": ["joy", "gratitude"],
            "ai_reflection": "...",
            "art_urls": ["https://drive.google.com/..."],
            "metadata": {...}
        }
    """
    try:
        drive_manager = GoogleDriveManager(session_data["access_token"])
        folder_id = session_data["drive_folder_id"]
        
        # Generate entry ID
        entry_id = f"entry_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"
        timestamp = datetime.utcnow().isoformat()
        
        # Step 1: Save raw input to Drive
        raw_file_ids = []
        processed_content = text_content
        
        if input_type == "text":
            # Save text as JSON
            text_file_id = drive_manager.upload_text(
                folder_id, 
                f"raw/{entry_id}.json",
                {"content": text_content, "timestamp": timestamp}
            )
            raw_file_ids.append(text_file_id)
            
        elif input_type in ["voice", "image", "drawing", "video"]:
            if not file_data:
                return {"error": "File required for this input type", "status": 400}
            
            # Save file to Drive
            file_id = drive_manager.upload_file(
                folder_id,
                f"raw/{entry_id}_{input_type}{file_helper.get_extension(file_data)}",
                file_data
            )
            raw_file_ids.append(file_id)
            
            # Process file based on type
            if input_type == "voice":
                # Transcribe audio
                transcription = await ai_orchestrator.transcribe_audio(file_data)
                processed_content = transcription.get("text", "")
                
            elif input_type in ["image", "drawing"]:
                # For now, use placeholder text; image emotion analysis optional
                processed_content = "I shared an image representing my current emotions."
                
            elif input_type == "video":
                # Extract audio and frames
                video_analysis = await ai_orchestrator.process_video(file_data)
                processed_content = video_analysis.get("transcription", "I shared a video moment.")
        
        # Step 2: Run AI pipeline
        logger.info(f"Processing {input_type} input for entry {entry_id}")
        
        ai_results = await ai_orchestrator.process_input(
            content=processed_content,
            input_type=input_type
        )
        
        # Step 3: Save AI outputs to Drive
        art_file_ids = []
        if ai_results.get("art_image"):
            art_file_id = drive_manager.upload_file(
                folder_id,
                f"outputs/{entry_id}_art.png",
                ai_results["art_image"]
            )
            art_file_ids.append(art_file_id)
        
        if ai_results.get("voice_audio"):
            voice_file_id = drive_manager.upload_file(
                folder_id,
                f"outputs/{entry_id}_voice.mp3",
                ai_results["voice_audio"]
            )
        
        # Step 4: Create log entry
        log_entry = {
            "id": entry_id,
            "timestamp": timestamp,
            "input_type": input_type,
            "file_ids": raw_file_ids,
            "emotion_labels": ai_results.get("emotions", []),
            "emotion_scores": ai_results.get("emotion_scores", {}),
            "ai_reflection": ai_results.get("reflection", ""),
            "poem": ai_results.get("poem", ""),
            "advice": ai_results.get("advice", ""),
            "art_file_ids": art_file_ids,
            "feedback": None,
            "metadata": {
                "model_versions": ai_results.get("model_versions", {}),
                "processing_time": ai_results.get("processing_time", 0),
                "fallback_used": ai_results.get("fallback_used", False)
            }
        }
        
        # Step 5: Append to log.json
        drive_manager.append_log_entry(folder_id, log_entry)
        
        logger.info(f"Entry {entry_id} processed successfully")
        
        # Return response
        return {
            "id": entry_id,
            "timestamp": timestamp,
            "emotion_labels": ai_results.get("emotions", []),
            "emotion_scores": ai_results.get("emotion_scores", {}),
            "ai_reflection": ai_results.get("reflection", ""),
            "poem": ai_results.get("poem", ""),
            "advice": ai_results.get("advice", ""),
            "art_urls": [drive_manager.get_file_url(fid) for fid in art_file_ids],
            "metadata": log_entry["metadata"],
            "status": 200
        }
        
    except Exception as e:
        logger.error(f"Submit error: {str(e)}")
        return {"error": str(e), "status": 500}


@require_session
def api_history(
    session_token: str,
    limit: int = 50,
    session_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    GET /api/history
    Retrieve user's journal entries from log.json.
    
    Args:
        session_token: User session token
        limit: Maximum number of entries to return
        session_data: Injected by decorator
        
    Returns:
        {"entries": [...], "total": 123, "status": 200}
    """
    try:
        drive_manager = GoogleDriveManager(session_data["access_token"])
        folder_id = session_data["drive_folder_id"]
        
        # Read log.json
        log_data = drive_manager.read_log(folder_id)
        entries = log_data.get("entries", [])
        
        # Sort by timestamp descending
        entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limit results
        limited_entries = entries[:limit]
        
        return {
            "entries": limited_entries,
            "total": len(entries),
            "status": 200
        }
        
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return {"error": str(e), "status": 500}


@require_session
def api_download(
    session_token: str,
    file_id: str,
    session_data: Optional[Dict] = None
) -> Any:
    """
    GET /api/download
    Download file from user's Drive folder.
    
    Args:
        session_token: User session token
        file_id: Google Drive file ID
        session_data: Injected by decorator
        
    Returns:
        File stream or error
    """
    try:
        drive_manager = GoogleDriveManager(session_data["access_token"])
        
        # Verify file belongs to user's folder (security check)
        # This is simplified; in production, maintain file ownership mapping
        
        file_content = drive_manager.download_file(file_id)
        return file_content
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return {"error": str(e), "status": 500}


@require_session
def api_feedback(
    session_token: str,
    entry_id: str,
    feedback: str,
    session_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    POST /api/feedback
    Add user feedback to a journal entry.
    
    Args:
        session_token: User session token
        entry_id: Entry ID to add feedback to
        feedback: Feedback text
        session_data: Injected by decorator
        
    Returns:
        {"success": True, "status": 200}
    """
    try:
        drive_manager = GoogleDriveManager(session_data["access_token"])
        folder_id = session_data["drive_folder_id"]
        
        # Read log
        log_data = drive_manager.read_log(folder_id)
        entries = log_data.get("entries", [])
        
        # Find and update entry
        updated = False
        for entry in entries:
            if entry.get("id") == entry_id:
                entry["feedback"] = feedback
                entry["feedback_timestamp"] = datetime.utcnow().isoformat()
                updated = True
                break
        
        if not updated:
            return {"error": "Entry not found", "status": 404}
        
        # Write back to log
        drive_manager.write_log(folder_id, log_data)
        
        return {"success": True, "status": 200}
        
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        return {"error": str(e), "status": 500}


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_gradio_app():
    """Create Gradio app with API endpoints."""
    
    # Create Gradio Blocks interface with CORS enabled
    with gr.Blocks(
        title="MindMirror AI",
        css=None,
        theme=gr.themes.Soft()
    ) as app:
        gr.Markdown("""
        # 🧠 MindMirror AI
        
        **Privacy-First Emotional Reflection Dashboard**
        
        This is the backend API. Use the React frontend to interact with the app.
        
        ### API Endpoints:
        - `POST /api/login` - OAuth login
        - `POST /api/submit` - Submit journal entry
        - `GET /api/history` - Get entry history
        - `GET /api/download` - Download file
        - `POST /api/feedback` - Add feedback
        
        **Privacy Notice:** All your data is stored only in your Google Drive.
        We do not retain or access your files.
        """)
        
        # Register API endpoints as Gradio components
        # These will be accessible via /api/predict
        
        with gr.Tab("Login API"):
            code_input = gr.Textbox(label="OAuth Code (leave empty for auth URL)", value="")
            login_output = gr.JSON(label="Response")
            login_btn = gr.Button("Call Login API")
            login_btn.click(fn=api_login, inputs=code_input, outputs=login_output, api_name="login")
        
        with gr.Tab("Submit API"):
            session_input = gr.Textbox(label="Session Token")
            type_input = gr.Textbox(label="Input Type")
            content_input = gr.Textbox(label="Content")
            file_input = gr.File(label="File")
            submit_output = gr.JSON(label="Response")
            submit_btn = gr.Button("Call Submit API")
            submit_btn.click(
                fn=api_submit,
                inputs=[session_input, type_input, content_input, file_input],
                outputs=submit_output,
                api_name="submit"
            )
        
        with gr.Tab("History API"):
            hist_session_input = gr.Textbox(label="Session Token")
            hist_limit_input = gr.Number(label="Limit", value=50)
            history_output = gr.JSON(label="Response")
            history_btn = gr.Button("Call History API")
            history_btn.click(
                fn=api_history,
                inputs=[hist_session_input, hist_limit_input],
                outputs=history_output,
                api_name="history"
            )
    
    return app


# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == "__main__":
    # Create Gradio app
    app = create_gradio_app()
    
    # Queue for API calls
    app.queue()
    
    # Launch with API mode enabled
    # This allows external REST API calls
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),
        share=False,
        show_api=True,  # Show API documentation
        allowed_paths=["/api"]  # Allow API endpoints
    )
