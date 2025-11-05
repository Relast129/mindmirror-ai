"""
Reflection Router for MindMirror AI
Generates AI-powered emotional reflections, poetry, and art
"""

from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
import logging
import json
from datetime import datetime
from utils.auth import get_current_user
from utils.google_drive import GoogleDriveManager
from ai.emotion_detector import EmotionDetector
from ai.poetry_generator import PoetryGenerator
from ai.art_generator import ArtGenerator
from ai.voice_processor import VoiceProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

class ReflectionRequest(BaseModel):
    """Request model for generating reflection"""
    content: str
    content_type: str = "text"  # text, voice_transcription, image_caption
    generate_art: bool = True
    generate_voice: bool = False

class ReflectionResponse(BaseModel):
    """Response model for reflection"""
    reflection_id: str
    emotion: str
    emotion_confidence: float
    emotion_summary: str
    reflection_text: str
    poem: str
    advice: str
    art_base64: Optional[str] = None
    voice_base64: Optional[str] = None
    color: str
    emoji: str
    timestamp: str

@router.post("/", response_model=ReflectionResponse)
async def generate_reflection(
    request: ReflectionRequest,
    google_token: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate complete AI reflection from user input
    
    Args:
        request: User content and preferences
        google_token: Google OAuth token
        current_user: Authenticated user
        
    Returns:
        Complete reflection with emotion analysis, poetry, and art
    """
    try:
        logger.info(f"Generating reflection for user: {current_user['email']}")
        
        # Step 1: Detect emotion
        emotion_detector = EmotionDetector()
        emotion_result = await emotion_detector.detect_emotion(request.content)
        
        primary_emotion = emotion_result['primary_emotion']
        confidence = emotion_result['confidence']
        emotion_summary = emotion_result['emotion_summary']
        
        logger.info(f"Detected emotion: {primary_emotion} (confidence: {confidence:.2f})")
        
        # Step 2: Generate poetic reflection
        poetry_generator = PoetryGenerator()
        poetry_result = await poetry_generator.generate_reflection(
            user_input=request.content,
            emotion=primary_emotion
        )
        
        # Step 3: Generate mood-based art (if requested)
        art_base64 = None
        if request.generate_art:
            try:
                art_generator = ArtGenerator()
                art_result = await art_generator.generate_mood_art(
                    emotion=primary_emotion,
                    user_input=request.content
                )
                
                if art_result['success']:
                    art_base64 = art_result['image_base64']
                    logger.info("AI art generated successfully")
            except Exception as e:
                logger.warning(f"Could not generate art: {str(e)}")
        
        # Step 4: Generate voice reflection (if requested)
        voice_base64 = None
        if request.generate_voice:
            try:
                voice_processor = VoiceProcessor()
                voice_text = f"{poetry_result['reflection']} {poetry_result['advice']}"
                voice_result = voice_processor.generate_speech(voice_text)
                
                if voice_result['success']:
                    voice_base64 = voice_result['audio_base64']
                    logger.info("Voice reflection generated successfully")
            except Exception as e:
                logger.warning(f"Could not generate voice: {str(e)}")
        
        # Step 5: Save reflection to Google Drive
        timestamp = datetime.now().isoformat()
        reflection_id = f"reflection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        reflection_data = {
            "reflection_id": reflection_id,
            "user_id": current_user['user_id'],
            "timestamp": timestamp,
            "original_content": request.content,
            "content_type": request.content_type,
            "emotion": {
                "primary": primary_emotion,
                "confidence": confidence,
                "summary": emotion_summary,
                "all_emotions": emotion_result.get('all_emotions', [])
            },
            "reflection": {
                "text": poetry_result['reflection'],
                "poem": poetry_result['poem'],
                "advice": poetry_result['advice']
            },
            "has_art": art_base64 is not None,
            "has_voice": voice_base64 is not None
        }
        
        try:
            drive_manager = GoogleDriveManager(google_token)
            app_folder_id = drive_manager.get_or_create_app_folder()
            reflections_folder_id = drive_manager.create_subfolder(app_folder_id, "Reflections")
            
            # Save reflection metadata
            drive_manager.upload_file_content(
                content=json.dumps(reflection_data, indent=2).encode('utf-8'),
                file_name=f"{reflection_id}.json",
                folder_id=reflections_folder_id,
                mime_type='application/json'
            )
            
            # Save art if generated
            if art_base64:
                art_folder_id = drive_manager.create_subfolder(app_folder_id, "AI Generated Art")
                import base64
                art_bytes = base64.b64decode(art_base64)
                drive_manager.upload_file_content(
                    content=art_bytes,
                    file_name=f"{reflection_id}_art.png",
                    folder_id=art_folder_id,
                    mime_type='image/png'
                )
            
            logger.info(f"Reflection saved to Drive: {reflection_id}")
        except Exception as e:
            logger.warning(f"Could not save to Drive: {str(e)}")
        
        # Get emotion color and emoji
        color = emotion_detector.get_emotion_color(primary_emotion)
        emoji = emotion_detector.get_emotion_emoji(primary_emotion)
        
        return ReflectionResponse(
            reflection_id=reflection_id,
            emotion=primary_emotion,
            emotion_confidence=confidence,
            emotion_summary=emotion_summary,
            reflection_text=poetry_result['reflection'],
            poem=poetry_result['poem'],
            advice=poetry_result['advice'],
            art_base64=art_base64,
            voice_base64=voice_base64,
            color=color,
            emoji=emoji,
            timestamp=timestamp
        )
        
    except Exception as e:
        logger.error(f"Error generating reflection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate reflection")

@router.get("/{reflection_id}")
async def get_reflection(
    reflection_id: str,
    google_token: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve a specific reflection by ID
    
    Args:
        reflection_id: Unique reflection identifier
        google_token: Google OAuth token
        current_user: Authenticated user
        
    Returns:
        Reflection data
    """
    try:
        drive_manager = GoogleDriveManager(google_token)
        app_folder_id = drive_manager.get_or_create_app_folder()
        reflections_folder_id = drive_manager.create_subfolder(app_folder_id, "Reflections")
        
        # List files and find the reflection
        files = drive_manager.list_files(reflections_folder_id)
        
        reflection_file = None
        for file in files:
            if file['name'] == f"{reflection_id}.json":
                reflection_file = file
                break
        
        if not reflection_file:
            raise HTTPException(status_code=404, detail="Reflection not found")
        
        # Download and parse reflection
        file_content = drive_manager.download_file(reflection_file['id'])
        reflection_data = json.loads(file_content.decode('utf-8'))
        
        return reflection_data
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving reflection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve reflection")

@router.post("/quick")
async def quick_emotion_check(
    content: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Quick emotion detection without full reflection generation
    
    Args:
        content: Text to analyze
        current_user: Authenticated user
        
    Returns:
        Emotion analysis only
    """
    try:
        emotion_detector = EmotionDetector()
        emotion_result = await emotion_detector.detect_emotion(content)
        
        return {
            "emotion": emotion_result['primary_emotion'],
            "confidence": emotion_result['confidence'],
            "summary": emotion_result['emotion_summary'],
            "color": emotion_detector.get_emotion_color(emotion_result['primary_emotion']),
            "emoji": emotion_detector.get_emotion_emoji(emotion_result['primary_emotion']),
            "all_emotions": emotion_result.get('all_emotions', [])
        }
        
    except Exception as e:
        logger.error(f"Error in quick emotion check: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze emotion")
