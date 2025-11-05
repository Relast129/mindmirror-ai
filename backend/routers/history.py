"""
History Router for MindMirror AI
Retrieves mood history, gallery, and statistics
"""

from fastapi import APIRouter, Depends, HTTPException, Form, Query
from pydantic import BaseModel
from typing import List, Optional
import logging
import json
from datetime import datetime, timedelta
from collections import Counter
from utils.auth import get_current_user
from utils.google_drive import GoogleDriveManager

logger = logging.getLogger(__name__)
router = APIRouter()

class MoodEntry(BaseModel):
    """Model for mood timeline entry"""
    timestamp: str
    emotion: str
    confidence: float
    reflection_id: str
    content_preview: str

class GalleryItem(BaseModel):
    """Model for gallery item"""
    id: str
    type: str  # reflection, art, image, video
    timestamp: str
    emotion: Optional[str] = None
    preview_url: Optional[str] = None
    thumbnail: Optional[str] = None

class UserStats(BaseModel):
    """Model for user statistics"""
    total_entries: int
    total_reflections: int
    current_streak: int
    longest_streak: int
    most_common_emotion: str
    emotion_distribution: dict
    entries_by_type: dict
    last_entry_date: Optional[str] = None

@router.get("/moods", response_model=List[MoodEntry])
async def get_mood_timeline(
    google_token: str = Query(...),
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user)
):
    """
    Get mood timeline for specified number of days
    
    Args:
        google_token: Google OAuth token
        days: Number of days to retrieve (default: 30)
        current_user: Authenticated user
        
    Returns:
        List of mood entries
    """
    try:
        drive_manager = GoogleDriveManager(google_token)
        app_folder_id = drive_manager.get_or_create_app_folder()
        reflections_folder_id = drive_manager.create_subfolder(app_folder_id, "Reflections")
        
        # Get all reflection files
        files = drive_manager.list_files(reflections_folder_id, page_size=1000)
        
        mood_entries = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for file in files:
            if not file['name'].endswith('.json'):
                continue
            
            try:
                # Download and parse reflection
                file_content = drive_manager.download_file(file['id'])
                reflection_data = json.loads(file_content.decode('utf-8'))
                
                # Check if within date range
                entry_date = datetime.fromisoformat(reflection_data['timestamp'])
                if entry_date < cutoff_date:
                    continue
                
                # Extract mood information
                emotion_data = reflection_data.get('emotion', {})
                original_content = reflection_data.get('original_content', '')
                
                mood_entry = MoodEntry(
                    timestamp=reflection_data['timestamp'],
                    emotion=emotion_data.get('primary', 'neutral'),
                    confidence=emotion_data.get('confidence', 0.0),
                    reflection_id=reflection_data['reflection_id'],
                    content_preview=original_content[:100] + '...' if len(original_content) > 100 else original_content
                )
                
                mood_entries.append(mood_entry)
                
            except Exception as e:
                logger.warning(f"Could not parse reflection file {file['name']}: {str(e)}")
                continue
        
        # Sort by timestamp (newest first)
        mood_entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        logger.info(f"Retrieved {len(mood_entries)} mood entries for user {current_user['email']}")
        return mood_entries
        
    except Exception as e:
        logger.error(f"Error retrieving mood timeline: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mood timeline")

@router.get("/gallery", response_model=List[GalleryItem])
async def get_emotional_gallery(
    google_token: str = Query(...),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """
    Get emotional gallery (reflections, art, images, videos)
    
    Args:
        google_token: Google OAuth token
        limit: Maximum number of items to return
        current_user: Authenticated user
        
    Returns:
        List of gallery items
    """
    try:
        drive_manager = GoogleDriveManager(google_token)
        app_folder_id = drive_manager.get_or_create_app_folder()
        
        gallery_items = []
        
        # Get AI generated art
        try:
            art_folder_id = drive_manager.create_subfolder(app_folder_id, "AI Generated Art")
            art_files = drive_manager.list_files(art_folder_id, page_size=limit)
            
            for file in art_files:
                gallery_items.append(GalleryItem(
                    id=file['id'],
                    type='art',
                    timestamp=file['createdTime'],
                    preview_url=file.get('webViewLink'),
                    thumbnail=file.get('thumbnailLink')
                ))
        except Exception as e:
            logger.warning(f"Could not retrieve art files: {str(e)}")
        
        # Get user images
        try:
            image_folder_id = drive_manager.create_subfolder(app_folder_id, "Images")
            image_files = drive_manager.list_files(image_folder_id, page_size=limit)
            
            for file in image_files:
                if not file['name'].endswith('.json'):  # Skip metadata files
                    gallery_items.append(GalleryItem(
                        id=file['id'],
                        type='image',
                        timestamp=file['createdTime'],
                        preview_url=file.get('webViewLink'),
                        thumbnail=file.get('thumbnailLink')
                    ))
        except Exception as e:
            logger.warning(f"Could not retrieve image files: {str(e)}")
        
        # Get videos
        try:
            video_folder_id = drive_manager.create_subfolder(app_folder_id, "Videos")
            video_files = drive_manager.list_files(video_folder_id, page_size=limit)
            
            for file in video_files:
                if not file['name'].endswith('.json'):
                    gallery_items.append(GalleryItem(
                        id=file['id'],
                        type='video',
                        timestamp=file['createdTime'],
                        preview_url=file.get('webViewLink')
                    ))
        except Exception as e:
            logger.warning(f"Could not retrieve video files: {str(e)}")
        
        # Sort by timestamp (newest first)
        gallery_items.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Limit results
        gallery_items = gallery_items[:limit]
        
        logger.info(f"Retrieved {len(gallery_items)} gallery items for user {current_user['email']}")
        return gallery_items
        
    except Exception as e:
        logger.error(f"Error retrieving gallery: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve gallery")

@router.get("/stats", response_model=UserStats)
async def get_user_statistics(
    google_token: str = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user statistics and insights
    
    Args:
        google_token: Google OAuth token
        current_user: Authenticated user
        
    Returns:
        User statistics
    """
    try:
        drive_manager = GoogleDriveManager(google_token)
        app_folder_id = drive_manager.get_or_create_app_folder()
        
        # Initialize counters
        total_entries = 0
        total_reflections = 0
        emotions = []
        entry_dates = []
        entries_by_type = {
            'text': 0,
            'voice': 0,
            'image': 0,
            'video': 0
        }
        
        # Count reflections
        try:
            reflections_folder_id = drive_manager.create_subfolder(app_folder_id, "Reflections")
            reflection_files = drive_manager.list_files(reflections_folder_id, page_size=1000)
            
            for file in reflection_files:
                if not file['name'].endswith('.json'):
                    continue
                
                try:
                    file_content = drive_manager.download_file(file['id'])
                    reflection_data = json.loads(file_content.decode('utf-8'))
                    
                    total_reflections += 1
                    
                    # Extract emotion
                    emotion_data = reflection_data.get('emotion', {})
                    emotions.append(emotion_data.get('primary', 'neutral'))
                    
                    # Extract date
                    timestamp = datetime.fromisoformat(reflection_data['timestamp'])
                    entry_dates.append(timestamp.date())
                    
                    # Count by type
                    content_type = reflection_data.get('content_type', 'text')
                    if content_type in entries_by_type:
                        entries_by_type[content_type] += 1
                    
                except Exception as e:
                    logger.warning(f"Could not parse reflection: {str(e)}")
                    continue
        except Exception as e:
            logger.warning(f"Could not retrieve reflections: {str(e)}")
        
        # Count other entries
        for folder_name, entry_type in [
            ("Text Journals", "text"),
            ("Voice Notes", "voice"),
            ("Images", "image"),
            ("Videos", "video")
        ]:
            try:
                folder_id = drive_manager.create_subfolder(app_folder_id, folder_name)
                files = drive_manager.list_files(folder_id, page_size=1000)
                
                # Count non-metadata files
                count = sum(1 for f in files if not f['name'].endswith('.json') or folder_name == "Text Journals")
                total_entries += count
                
            except Exception as e:
                logger.warning(f"Could not count {folder_name}: {str(e)}")
        
        # Calculate streaks
        current_streak = 0
        longest_streak = 0
        
        if entry_dates:
            entry_dates.sort(reverse=True)
            unique_dates = sorted(set(entry_dates), reverse=True)
            
            # Calculate current streak
            today = datetime.now().date()
            if unique_dates and unique_dates[0] >= today - timedelta(days=1):
                current_streak = 1
                for i in range(1, len(unique_dates)):
                    if unique_dates[i] == unique_dates[i-1] - timedelta(days=1):
                        current_streak += 1
                    else:
                        break
            
            # Calculate longest streak
            temp_streak = 1
            for i in range(1, len(unique_dates)):
                if unique_dates[i] == unique_dates[i-1] - timedelta(days=1):
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 1
            longest_streak = max(longest_streak, temp_streak)
        
        # Emotion distribution
        emotion_counter = Counter(emotions)
        most_common_emotion = emotion_counter.most_common(1)[0][0] if emotions else "neutral"
        emotion_distribution = dict(emotion_counter)
        
        # Last entry date
        last_entry_date = entry_dates[0].isoformat() if entry_dates else None
        
        stats = UserStats(
            total_entries=total_entries,
            total_reflections=total_reflections,
            current_streak=current_streak,
            longest_streak=longest_streak,
            most_common_emotion=most_common_emotion,
            emotion_distribution=emotion_distribution,
            entries_by_type=entries_by_type,
            last_entry_date=last_entry_date
        )
        
        logger.info(f"Retrieved statistics for user {current_user['email']}")
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

@router.get("/export")
async def export_user_data(
    google_token: str = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Export all user data as JSON
    
    Args:
        google_token: Google OAuth token
        current_user: Authenticated user
        
    Returns:
        Complete user data export
    """
    try:
        # Get all data
        moods = await get_mood_timeline(google_token, 365, current_user)
        gallery = await get_emotional_gallery(google_token, 1000, current_user)
        stats = await get_user_statistics(google_token, current_user)
        
        export_data = {
            "user_id": current_user['user_id'],
            "email": current_user['email'],
            "export_date": datetime.now().isoformat(),
            "statistics": stats.dict(),
            "mood_timeline": [m.dict() for m in moods],
            "gallery": [g.dict() for g in gallery]
        }
        
        logger.info(f"Exported data for user {current_user['email']}")
        return export_data
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export data")
