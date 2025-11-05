"""
Upload Router for MindMirror AI
Handles multi-modal file uploads (text, voice, images, videos)
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import json
from datetime import datetime
from utils.auth import get_current_user
from utils.google_drive import GoogleDriveManager
from utils.file_handler import FileHandler
from ai.voice_processor import VoiceProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

class TextUploadRequest(BaseModel):
    """Request model for text journal upload"""
    content: str
    title: Optional[str] = None
    tags: Optional[list] = []

class UploadResponse(BaseModel):
    """Response model for uploads"""
    success: bool
    file_id: str
    file_name: str
    message: str
    transcription: Optional[str] = None

@router.post("/text", response_model=UploadResponse)
async def upload_text(
    request: TextUploadRequest,
    current_user: dict = Depends(get_current_user),
    google_token: str = Form(...)
):
    """
    Upload text journal entry
    
    Args:
        request: Text content and metadata
        current_user: Authenticated user
        google_token: Google OAuth token for Drive access
        
    Returns:
        Upload confirmation with file ID
    """
    try:
        # Initialize Drive manager
        drive_manager = GoogleDriveManager(google_token)
        app_folder_id = drive_manager.get_or_create_app_folder()
        text_folder_id = drive_manager.create_subfolder(app_folder_id, "Text Journals")
        
        # Create file content
        timestamp = datetime.now().isoformat()
        file_content = {
            "title": request.title or f"Journal Entry - {timestamp}",
            "content": request.content,
            "tags": request.tags,
            "timestamp": timestamp,
            "user_id": current_user['user_id']
        }
        
        # Generate filename
        file_name = f"journal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Upload to Drive
        file_info = drive_manager.upload_file_content(
            content=json.dumps(file_content, indent=2).encode('utf-8'),
            file_name=file_name,
            folder_id=text_folder_id,
            mime_type='application/json',
            metadata={"type": "text_journal", "timestamp": timestamp}
        )
        
        logger.info(f"Text uploaded for user {current_user['email']}: {file_info['id']}")
        
        return UploadResponse(
            success=True,
            file_id=file_info['id'],
            file_name=file_info['name'],
            message="Text journal saved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error uploading text: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload text")

@router.post("/voice", response_model=UploadResponse)
async def upload_voice(
    file: UploadFile = File(...),
    google_token: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload voice recording and transcribe it
    
    Args:
        file: Audio file
        google_token: Google OAuth token
        current_user: Authenticated user
        
    Returns:
        Upload confirmation with transcription
    """
    try:
        # Validate audio file
        FileHandler.validate_audio(file)
        
        # Save to temporary location
        tmp_path = await FileHandler.save_upload_file_tmp(file)
        
        # Transcribe audio
        voice_processor = VoiceProcessor()
        transcription_result = await voice_processor.transcribe_audio(tmp_path)
        
        # Initialize Drive manager
        drive_manager = GoogleDriveManager(google_token)
        app_folder_id = drive_manager.get_or_create_app_folder()
        voice_folder_id = drive_manager.create_subfolder(app_folder_id, "Voice Notes")
        
        # Upload original audio
        timestamp = datetime.now().isoformat()
        file_name = f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}{FileHandler.get_mime_type(file.filename).split('/')[-1]}"
        
        file_info = drive_manager.upload_file(
            file_path=tmp_path,
            file_name=file_name,
            folder_id=voice_folder_id,
            mime_type=FileHandler.get_mime_type(file.filename),
            metadata={
                "type": "voice_note",
                "timestamp": timestamp,
                "transcription": transcription_result['transcription']
            }
        )
        
        # Also save transcription as text
        transcription_content = {
            "transcription": transcription_result['transcription'],
            "language": transcription_result.get('language', 'en'),
            "confidence": transcription_result.get('confidence', 0.0),
            "timestamp": timestamp,
            "audio_file_id": file_info['id'],
            "user_id": current_user['user_id']
        }
        
        drive_manager.upload_file_content(
            content=json.dumps(transcription_content, indent=2).encode('utf-8'),
            file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            folder_id=voice_folder_id,
            mime_type='application/json'
        )
        
        # Clean up temporary file
        FileHandler.cleanup_temp_file(tmp_path)
        
        logger.info(f"Voice uploaded for user {current_user['email']}: {file_info['id']}")
        
        return UploadResponse(
            success=True,
            file_id=file_info['id'],
            file_name=file_info['name'],
            message="Voice note saved and transcribed successfully",
            transcription=transcription_result['transcription']
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error uploading voice: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload voice")

@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    google_token: str = Form(...),
    caption: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload image or drawing
    
    Args:
        file: Image file
        google_token: Google OAuth token
        caption: Optional caption
        current_user: Authenticated user
        
    Returns:
        Upload confirmation
    """
    try:
        # Validate image file
        FileHandler.validate_image(file)
        
        # Save to temporary location
        tmp_path = await FileHandler.save_upload_file_tmp(file)
        
        # Initialize Drive manager
        drive_manager = GoogleDriveManager(google_token)
        app_folder_id = drive_manager.get_or_create_app_folder()
        image_folder_id = drive_manager.create_subfolder(app_folder_id, "Images")
        
        # Upload image
        timestamp = datetime.now().isoformat()
        file_name = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(file.filename)[1]}"
        
        file_info = drive_manager.upload_file(
            file_path=tmp_path,
            file_name=file_name,
            folder_id=image_folder_id,
            mime_type=FileHandler.get_mime_type(file.filename),
            metadata={
                "type": "image",
                "timestamp": timestamp,
                "caption": caption or ""
            }
        )
        
        # Save metadata
        if caption:
            metadata_content = {
                "image_file_id": file_info['id'],
                "caption": caption,
                "timestamp": timestamp,
                "user_id": current_user['user_id']
            }
            
            drive_manager.upload_file_content(
                content=json.dumps(metadata_content, indent=2).encode('utf-8'),
                file_name=f"image_meta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                folder_id=image_folder_id,
                mime_type='application/json'
            )
        
        # Clean up temporary file
        FileHandler.cleanup_temp_file(tmp_path)
        
        logger.info(f"Image uploaded for user {current_user['email']}: {file_info['id']}")
        
        return UploadResponse(
            success=True,
            file_id=file_info['id'],
            file_name=file_info['name'],
            message="Image saved successfully"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload image")

@router.post("/video", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    google_token: str = Form(...),
    caption: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload video clip
    
    Args:
        file: Video file
        google_token: Google OAuth token
        caption: Optional caption
        current_user: Authenticated user
        
    Returns:
        Upload confirmation with optional transcription
    """
    try:
        # Validate video file
        FileHandler.validate_video(file)
        
        # Save to temporary location
        tmp_path = await FileHandler.save_upload_file_tmp(file)
        
        # Initialize Drive manager
        drive_manager = GoogleDriveManager(google_token)
        app_folder_id = drive_manager.get_or_create_app_folder()
        video_folder_id = drive_manager.create_subfolder(app_folder_id, "Videos")
        
        # Upload video
        timestamp = datetime.now().isoformat()
        file_name = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(file.filename)[1]}"
        
        file_info = drive_manager.upload_file(
            file_path=tmp_path,
            file_name=file_name,
            folder_id=video_folder_id,
            mime_type=FileHandler.get_mime_type(file.filename),
            metadata={
                "type": "video",
                "timestamp": timestamp,
                "caption": caption or ""
            }
        )
        
        # Optional: Extract and transcribe audio from video
        transcription = None
        try:
            voice_processor = VoiceProcessor()
            transcription_result = await voice_processor.process_video_audio(tmp_path)
            if transcription_result['success']:
                transcription = transcription_result['transcription']
        except Exception as e:
            logger.warning(f"Could not transcribe video audio: {str(e)}")
        
        # Clean up temporary file
        FileHandler.cleanup_temp_file(tmp_path)
        
        logger.info(f"Video uploaded for user {current_user['email']}: {file_info['id']}")
        
        return UploadResponse(
            success=True,
            file_id=file_info['id'],
            file_name=file_info['name'],
            message="Video saved successfully",
            transcription=transcription
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload video")

import os
