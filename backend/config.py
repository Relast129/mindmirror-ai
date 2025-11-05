"""
Configuration settings for MindMirror AI
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MindMirror AI"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
    
    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Hugging Face
    HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "")
    
    # Google Drive
    DRIVE_FOLDER_NAME: str = "MindMirror AI Data"
    
    # AI Model Settings
    EMOTION_MODEL: str = "j-hartmann/emotion-english-distilroberta-base"
    POETRY_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.1"
    ART_MODEL: str = "stabilityai/stable-diffusion-2-1"
    
    # File Upload Limits (in bytes)
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    MAX_VOICE_SIZE: int = 10 * 1024 * 1024   # 10MB
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024   # 10MB
    MAX_VIDEO_SIZE: int = 50 * 1024 * 1024   # 50MB
    
    # Allowed file types
    ALLOWED_IMAGE_TYPES: list = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
    ALLOWED_AUDIO_TYPES: list = [".mp3", ".wav", ".m4a", ".ogg", ".webm"]
    ALLOWED_VIDEO_TYPES: list = [".mp4", ".mov", ".avi", ".webm"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
