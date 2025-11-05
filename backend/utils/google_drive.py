"""
Google Drive Manager for MindMirror AI - Gradio Version
Handles all Google Drive operations for privacy-first file storage.
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
from config import settings

logger = logging.getLogger(__name__)

class GoogleDriveManager:
    """Manages Google Drive operations for user data storage"""
    
    def __init__(self, access_token: str):
        """
        Initialize Google Drive manager with user's access token
        
        Args:
            access_token: Google OAuth access token
        """
        self.credentials = Credentials(token=access_token)
        self.service = build('drive', 'v3', credentials=self.credentials)
        
    def get_or_create_app_folder(self) -> str:
        """
        Get or create the MindMirror AI folder in user's Drive
        
        Returns:
            Folder ID
        """
        try:
            # Search for existing folder
            query = f"name='{settings.DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                logger.info(f"Found existing folder: {folders[0]['id']}")
                return folders[0]['id']
            
            # Create new folder
            folder_metadata = {
                'name': settings.DRIVE_FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder',
                'description': 'Private storage for MindMirror AI - Your emotional reflections and data'
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            logger.info(f"Created new folder: {folder['id']}")
            return folder['id']
            
        except HttpError as error:
            logger.error(f"Error managing app folder: {error}")
            raise
    
    def create_subfolder(self, parent_folder_id: str, folder_name: str) -> str:
        """
        Create a subfolder within the app folder
        
        Args:
            parent_folder_id: Parent folder ID
            folder_name: Name of subfolder to create
            
        Returns:
            Subfolder ID
        """
        try:
            # Check if subfolder exists
            query = f"name='{folder_name}' and '{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            if folders:
                return folders[0]['id']
            
            # Create subfolder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            return folder['id']
            
        except HttpError as error:
            logger.error(f"Error creating subfolder: {error}")
            raise
    
    def upload_file(
        self,
        file_path: str,
        file_name: str,
        folder_id: str,
        mime_type: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Upload a file to Google Drive
        
        Args:
            file_path: Local path to file
            file_name: Name for the file in Drive
            folder_id: Parent folder ID
            mime_type: MIME type of the file
            metadata: Optional additional metadata
            
        Returns:
            File information dictionary
        """
        try:
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            if metadata:
                file_metadata['description'] = str(metadata)
            
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, createdTime, size, webViewLink'
            ).execute()
            
            logger.info(f"Uploaded file: {file['name']} (ID: {file['id']})")
            return file
            
        except HttpError as error:
            logger.error(f"Error uploading file: {error}")
            raise
    
    def upload_file_content(
        self,
        content: bytes,
        file_name: str,
        folder_id: str,
        mime_type: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Upload file content directly to Google Drive
        
        Args:
            content: File content as bytes
            file_name: Name for the file in Drive
            folder_id: Parent folder ID
            mime_type: MIME type of the file
            metadata: Optional additional metadata
            
        Returns:
            File information dictionary
        """
        try:
            from googleapiclient.http import MediaInMemoryUpload
            
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            if metadata:
                file_metadata['description'] = str(metadata)
            
            media = MediaInMemoryUpload(content, mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, createdTime, size, webViewLink'
            ).execute()
            
            logger.info(f"Uploaded file content: {file['name']} (ID: {file['id']})")
            return file
            
        except HttpError as error:
            logger.error(f"Error uploading file content: {error}")
            raise
    
    def download_file(self, file_id: str) -> bytes:
        """
        Download a file from Google Drive
        
        Args:
            file_id: ID of the file to download
            
        Returns:
            File content as bytes
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logger.info(f"Download progress: {int(status.progress() * 100)}%")
            
            return file_content.getvalue()
            
        except HttpError as error:
            logger.error(f"Error downloading file: {error}")
            raise
    
    def list_files(
        self,
        folder_id: str,
        page_size: int = 100,
        order_by: str = 'createdTime desc'
    ) -> List[Dict]:
        """
        List files in a folder
        
        Args:
            folder_id: Folder ID to list files from
            page_size: Number of files per page
            order_by: Sort order
            
        Returns:
            List of file information dictionaries
        """
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                orderBy=order_by,
                fields='files(id, name, mimeType, createdTime, modifiedTime, size, webViewLink, description)'
            ).execute()
            
            files = results.get('files', [])
            return files
            
        except HttpError as error:
            logger.error(f"Error listing files: {error}")
            raise
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            True if successful
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted file: {file_id}")
            return True
            
        except HttpError as error:
            logger.error(f"Error deleting file: {error}")
            raise
    
    def get_file_metadata(self, file_id: str) -> Dict:
        """
        Get metadata for a file
        
        Args:
            file_id: ID of the file
            
        Returns:
            File metadata dictionary
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, createdTime, modifiedTime, size, webViewLink, description'
            ).execute()
            
            return file
            
        except HttpError as error:
            logger.error(f"Error getting file metadata: {error}")
            raise
