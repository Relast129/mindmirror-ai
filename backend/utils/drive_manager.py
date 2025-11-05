"""
Google Drive Manager for MindMirror AI - Gradio Version
Handles all Google Drive operations for privacy-first file storage.
No config dependency - standalone module.
"""

import os
import io
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

class GoogleDriveManager:
    """Manages Google Drive operations for user data storage."""
    
    APP_FOLDER_NAME = "MindMirrorAI"
    
    def __init__(self, access_token: str):
        """
        Initialize Google Drive manager with user's access token.
        
        Args:
            access_token: Google OAuth access token
        """
        self.credentials = Credentials(token=access_token)
        self.service = build('drive', 'v3', credentials=self.credentials)
    
    def create_user_folder(self, profile: Dict[str, Any]) -> str:
        """
        Create or get user's MindMirror AI folder structure.
        Creates: /MindMirrorAI/<username>_<id>/raw/ and /outputs/
        
        Args:
            profile: User profile dict with 'id', 'name', 'email'
            
        Returns:
            Root folder ID for user
        """
        try:
            user_id = profile.get("id", "unknown")
            user_name = profile.get("name", "user").replace(" ", "_")
            folder_name = f"{self.APP_FOLDER_NAME}/{user_name}_{user_id}"
            
            # Check if root app folder exists
            root_folder_id = self._get_or_create_folder(self.APP_FOLDER_NAME, None)
            
            # Check if user folder exists
            user_folder_id = self._get_or_create_folder(f"{user_name}_{user_id}", root_folder_id)
            
            # Create subfolders
            self._get_or_create_folder("raw", user_folder_id)
            self._get_or_create_folder("outputs", user_folder_id)
            
            # Create log.json if it doesn't exist
            self._ensure_log_file(user_folder_id)
            
            logger.info(f"User folder ready: {folder_name}")
            return user_folder_id
            
        except Exception as e:
            logger.error(f"Error creating user folder: {str(e)}")
            raise
    
    def _get_or_create_folder(self, folder_name: str, parent_id: Optional[str]) -> str:
        """Get or create a folder."""
        try:
            # Search for existing folder
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                return folders[0]['id']
            
            # Create new folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            logger.info(f"Created folder: {folder_name}")
            return folder['id']
            
        except Exception as e:
            logger.error(f"Error with folder {folder_name}: {str(e)}")
            raise
    
    def _ensure_log_file(self, folder_id: str):
        """Ensure log.json exists in folder."""
        try:
            # Check if log.json exists
            query = f"name='log.json' and '{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)'
            ).execute()
            
            if not results.get('files'):
                # Create empty log file
                initial_log = {"entries": [], "created_at": datetime.utcnow().isoformat()}
                self.upload_text(folder_id, "log.json", initial_log)
                
        except Exception as e:
            logger.error(f"Error ensuring log file: {str(e)}")
    
    def upload_file(self, folder_id: str, filename: str, file_data: Any) -> str:
        """
        Upload a file to Drive.
        
        Args:
            folder_id: Parent folder ID
            filename: Name for the file
            file_data: File data (bytes or file-like object)
            
        Returns:
            File ID
        """
        try:
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # Handle different file data types
            if isinstance(file_data, bytes):
                media = MediaIoBaseUpload(
                    io.BytesIO(file_data),
                    mimetype='application/octet-stream',
                    resumable=True
                )
            elif hasattr(file_data, 'read'):
                media = MediaIoBaseUpload(
                    file_data,
                    mimetype='application/octet-stream',
                    resumable=True
                )
            else:
                raise ValueError("Invalid file_data type")
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            logger.info(f"Uploaded file: {filename} (ID: {file['id']})")
            return file['id']
            
        except Exception as e:
            logger.error(f"Error uploading file {filename}: {str(e)}")
            raise
    
    def upload_text(self, folder_id: str, filename: str, data: Dict) -> str:
        """
        Upload JSON data as a file.
        
        Args:
            folder_id: Parent folder ID
            filename: Name for the file
            data: Dictionary to save as JSON
            
        Returns:
            File ID
        """
        try:
            json_str = json.dumps(data, indent=2)
            json_bytes = json_str.encode('utf-8')
            
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            media = MediaIoBaseUpload(
                io.BytesIO(json_bytes),
                mimetype='application/json',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            logger.info(f"Uploaded JSON file: {filename}")
            return file['id']
            
        except Exception as e:
            logger.error(f"Error uploading JSON {filename}: {str(e)}")
            raise
    
    def read_log(self, folder_id: str) -> Dict[str, Any]:
        """
        Read log.json from user's folder.
        
        Args:
            folder_id: User's root folder ID
            
        Returns:
            Log data dictionary
        """
        try:
            # Find log.json
            query = f"name='log.json' and '{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)'
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                # Create new log if doesn't exist
                initial_log = {"entries": [], "created_at": datetime.utcnow().isoformat()}
                self.upload_text(folder_id, "log.json", initial_log)
                return initial_log
            
            # Download and parse log
            file_id = files[0]['id']
            request = self.service.files().get_media(fileId=file_id)
            
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_buffer.seek(0)
            log_data = json.load(file_buffer)
            
            return log_data
            
        except Exception as e:
            logger.error(f"Error reading log: {str(e)}")
            return {"entries": [], "error": str(e)}
    
    def write_log(self, folder_id: str, log_data: Dict[str, Any]):
        """
        Write log.json to user's folder (overwrites existing).
        
        Args:
            folder_id: User's root folder ID
            log_data: Log data to write
        """
        try:
            # Find existing log.json
            query = f"name='log.json' and '{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)'
            ).execute()
            
            files = results.get('files', [])
            
            json_str = json.dumps(log_data, indent=2)
            json_bytes = json_str.encode('utf-8')
            
            media = MediaIoBaseUpload(
                io.BytesIO(json_bytes),
                mimetype='application/json',
                resumable=True
            )
            
            if files:
                # Update existing file
                file_id = files[0]['id']
                self.service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()
                logger.info("Updated log.json")
            else:
                # Create new file
                file_metadata = {
                    'name': 'log.json',
                    'parents': [folder_id]
                }
                self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info("Created log.json")
                
        except Exception as e:
            logger.error(f"Error writing log: {str(e)}")
            raise
    
    def append_log_entry(self, folder_id: str, entry: Dict[str, Any]):
        """
        Append an entry to log.json.
        
        Args:
            folder_id: User's root folder ID
            entry: Entry dictionary to append
        """
        try:
            log_data = self.read_log(folder_id)
            
            if "entries" not in log_data:
                log_data["entries"] = []
            
            log_data["entries"].append(entry)
            log_data["last_updated"] = datetime.utcnow().isoformat()
            
            self.write_log(folder_id, log_data)
            logger.info(f"Appended entry {entry.get('id')} to log")
            
        except Exception as e:
            logger.error(f"Error appending log entry: {str(e)}")
            raise
    
    def download_file(self, file_id: str) -> bytes:
        """
        Download a file from Drive.
        
        Args:
            file_id: File ID to download
            
        Returns:
            File bytes
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_buffer.seek(0)
            return file_buffer.read()
            
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {str(e)}")
            raise
    
    def get_file_url(self, file_id: str) -> str:
        """
        Get shareable URL for a file.
        
        Args:
            file_id: File ID
            
        Returns:
            URL string
        """
        return f"https://drive.google.com/file/d/{file_id}/view"
    
    def list_files(self, folder_id: str, file_type: Optional[str] = None) -> List[Dict]:
        """
        List files in a folder.
        
        Args:
            folder_id: Folder ID
            file_type: Optional filter by file type
            
        Returns:
            List of file metadata dicts
        """
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            if file_type:
                query += f" and mimeType contains '{file_type}'"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, createdTime, size)',
                orderBy='createdTime desc'
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []
