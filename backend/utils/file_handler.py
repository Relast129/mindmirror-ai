"""
File handling utilities for MindMirror AI
Processes and validates uploaded files
"""

import os
import tempfile
import mimetypes
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from config import settings
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles file validation and processing"""
    
    @staticmethod
    def validate_file_size(file: UploadFile, max_size: int) -> bool:
        """
        Validate file size
        
        Args:
            file: Uploaded file
            max_size: Maximum allowed size in bytes
            
        Returns:
            True if valid
            
        Raises:
            HTTPException: If file is too large
        """
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {max_size / (1024*1024):.1f}MB"
            )
        
        return True
    
    @staticmethod
    def validate_file_type(file: UploadFile, allowed_types: list) -> bool:
        """
        Validate file type
        
        Args:
            file: Uploaded file
            allowed_types: List of allowed file extensions
            
        Returns:
            True if valid
            
        Raises:
            HTTPException: If file type not allowed
        """
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=415,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        return True
    
    @staticmethod
    async def save_upload_file_tmp(upload_file: UploadFile) -> str:
        """
        Save uploaded file to temporary location
        
        Args:
            upload_file: FastAPI UploadFile object
            
        Returns:
            Path to temporary file
        """
        try:
            suffix = os.path.splitext(upload_file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await upload_file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            logger.info(f"Saved upload to temporary file: {tmp_path}")
            return tmp_path
            
        except Exception as e:
            logger.error(f"Error saving upload file: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing file")
    
    @staticmethod
    def get_mime_type(filename: str) -> str:
        """
        Get MIME type from filename
        
        Args:
            filename: Name of the file
            
        Returns:
            MIME type string
        """
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """
        Delete temporary file
        
        Args:
            file_path: Path to temporary file
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Could not delete temporary file {file_path}: {str(e)}")
    
    @staticmethod
    def validate_image(file: UploadFile) -> bool:
        """
        Validate image file
        
        Args:
            file: Uploaded image file
            
        Returns:
            True if valid
        """
        FileHandler.validate_file_size(file, settings.MAX_IMAGE_SIZE)
        FileHandler.validate_file_type(file, settings.ALLOWED_IMAGE_TYPES)
        return True
    
    @staticmethod
    def validate_audio(file: UploadFile) -> bool:
        """
        Validate audio file
        
        Args:
            file: Uploaded audio file
            
        Returns:
            True if valid
        """
        FileHandler.validate_file_size(file, settings.MAX_VOICE_SIZE)
        FileHandler.validate_file_type(file, settings.ALLOWED_AUDIO_TYPES)
        return True
    
    @staticmethod
    def validate_video(file: UploadFile) -> bool:
        """
        Validate video file
        
        Args:
            file: Uploaded video file
            
        Returns:
            True if valid
        """
        FileHandler.validate_file_size(file, settings.MAX_VIDEO_SIZE)
        FileHandler.validate_file_type(file, settings.ALLOWED_VIDEO_TYPES)
        return True
