"""
Authentication Router for MindMirror AI
Handles Google OAuth login and user session management
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from utils.auth import create_access_token, get_current_user, verify_google_token
from utils.google_drive import GoogleDriveManager
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class GoogleAuthRequest(BaseModel):
    """Request model for Google authentication"""
    token: str
    
class UserResponse(BaseModel):
    """Response model for user data"""
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    access_token: str

@router.post("/google", response_model=UserResponse)
async def google_auth(auth_request: GoogleAuthRequest):
    """
    Authenticate user with Google OAuth token
    
    Args:
        auth_request: Contains Google OAuth token
        
    Returns:
        User information and JWT access token
    """
    try:
        # Verify Google token
        user_info = verify_google_token(auth_request.token)
        
        # Create JWT access token
        access_token = create_access_token(
            data={
                "sub": user_info['user_id'],
                "email": user_info['email'],
                "name": user_info['name'],
                "picture": user_info.get('picture', '')
            }
        )
        
        # Initialize Google Drive for user
        try:
            drive_manager = GoogleDriveManager(auth_request.token)
            folder_id = drive_manager.get_or_create_app_folder()
            
            # Create subfolders for different content types
            drive_manager.create_subfolder(folder_id, "Text Journals")
            drive_manager.create_subfolder(folder_id, "Voice Notes")
            drive_manager.create_subfolder(folder_id, "Images")
            drive_manager.create_subfolder(folder_id, "Videos")
            drive_manager.create_subfolder(folder_id, "AI Generated Art")
            drive_manager.create_subfolder(folder_id, "Reflections")
            
            logger.info(f"Initialized Drive folders for user: {user_info['email']}")
        except Exception as e:
            logger.warning(f"Could not initialize Drive folders: {str(e)}")
        
        return UserResponse(
            user_id=user_info['user_id'],
            email=user_info['email'],
            name=user_info['name'],
            picture=user_info.get('picture'),
            access_token=access_token
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Returns:
        Current user data
    """
    return {
        "user_id": current_user['user_id'],
        "email": current_user['email'],
        "name": current_user['name'],
        "picture": current_user.get('picture')
    }

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user
    
    Returns:
        Success message
    """
    logger.info(f"User logged out: {current_user['email']}")
    return {"message": "Successfully logged out"}

@router.get("/callback")
async def auth_callback(code: str, state: Optional[str] = None):
    """
    OAuth callback endpoint (for server-side flow if needed)
    
    Args:
        code: Authorization code from Google
        state: Optional state parameter
        
    Returns:
        Redirect to frontend with token
    """
    try:
        # This is a placeholder for server-side OAuth flow
        # The main flow uses client-side Google Sign-In
        
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/success"
        )
        
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/error"
        )

@router.get("/health")
async def auth_health():
    """Health check for auth service"""
    return {
        "status": "healthy",
        "service": "authentication",
        "google_oauth": "configured" if settings.GOOGLE_CLIENT_ID else "not configured"
    }
