"""
File Helper Utilities
"""

import os
import mimetypes
from typing import Optional

class FileHelper:
    """Helper functions for file operations."""
    
    @staticmethod
    def get_extension(file_data) -> str:
        """
        Get file extension from file data.
        
        Args:
            file_data: File object or path
            
        Returns:
            Extension string (e.g., '.mp3')
        """
        if hasattr(file_data, 'name'):
            _, ext = os.path.splitext(file_data.name)
            return ext
        elif isinstance(file_data, str):
            _, ext = os.path.splitext(file_data)
            return ext
        return ''
    
    @staticmethod
    def get_mime_type(filename: str) -> str:
        """
        Get MIME type from filename.
        
        Args:
            filename: File name
            
        Returns:
            MIME type string
        """
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    @staticmethod
    def is_audio_file(filename: str) -> bool:
        """Check if file is audio."""
        audio_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.webm', '.flac']
        _, ext = os.path.splitext(filename.lower())
        return ext in audio_extensions
    
    @staticmethod
    def is_image_file(filename: str) -> bool:
        """Check if file is image."""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        _, ext = os.path.splitext(filename.lower())
        return ext in image_extensions
    
    @staticmethod
    def is_video_file(filename: str) -> bool:
        """Check if file is video."""
        video_extensions = ['.mp4', '.mov', '.avi', '.webm', '.mkv']
        _, ext = os.path.splitext(filename.lower())
        return ext in video_extensions
