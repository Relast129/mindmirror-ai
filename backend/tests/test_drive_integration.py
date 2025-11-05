"""
Integration tests for Google Drive
NOTE: Requires a test Google account with Drive API access
Set GOOGLE_TEST_ACCESS_TOKEN environment variable to run these tests
"""

import pytest
import os
import json
from utils.drive_manager import GoogleDriveManager

# Skip tests if no test token provided
pytestmark = pytest.mark.skipif(
    not os.getenv("GOOGLE_TEST_ACCESS_TOKEN"),
    reason="GOOGLE_TEST_ACCESS_TOKEN not set"
)

@pytest.fixture
def drive_manager():
    """Create Drive manager with test token."""
    token = os.getenv("GOOGLE_TEST_ACCESS_TOKEN")
    return GoogleDriveManager(token)

@pytest.fixture
def test_profile():
    """Test user profile."""
    return {
        "id": "test_user_123",
        "name": "Test User",
        "email": "test@example.com"
    }

def test_create_user_folder(drive_manager, test_profile):
    """Test creating user folder structure."""
    folder_id = drive_manager.create_user_folder(test_profile)
    
    assert folder_id is not None
    assert isinstance(folder_id, str)
    
    # Verify subfolders exist
    files = drive_manager.list_files(folder_id)
    folder_names = [f['name'] for f in files if f.get('mimeType') == 'application/vnd.google-apps.folder']
    
    assert 'raw' in folder_names
    assert 'outputs' in folder_names

def test_upload_and_read_log(drive_manager, test_profile):
    """Test log file operations."""
    folder_id = drive_manager.create_user_folder(test_profile)
    
    # Read initial log
    log_data = drive_manager.read_log(folder_id)
    assert "entries" in log_data
    assert isinstance(log_data["entries"], list)
    
    # Append entry
    test_entry = {
        "id": "test_entry_1",
        "timestamp": "2023-11-04T12:00:00",
        "emotion_labels": ["joy"],
        "ai_reflection": "Test reflection"
    }
    
    drive_manager.append_log_entry(folder_id, test_entry)
    
    # Read again
    updated_log = drive_manager.read_log(folder_id)
    assert len(updated_log["entries"]) > 0
    assert updated_log["entries"][-1]["id"] == "test_entry_1"

def test_upload_text_file(drive_manager, test_profile):
    """Test uploading JSON data."""
    folder_id = drive_manager.create_user_folder(test_profile)
    
    test_data = {
        "content": "Test journal entry",
        "timestamp": "2023-11-04T12:00:00"
    }
    
    file_id = drive_manager.upload_text(folder_id, "test.json", test_data)
    
    assert file_id is not None
    assert isinstance(file_id, str)

def test_upload_binary_file(drive_manager, test_profile):
    """Test uploading binary data."""
    folder_id = drive_manager.create_user_folder(test_profile)
    
    test_bytes = b"Test binary data"
    file_id = drive_manager.upload_file(folder_id, "test.bin", test_bytes)
    
    assert file_id is not None
    
    # Download and verify
    downloaded = drive_manager.download_file(file_id)
    assert downloaded == test_bytes

def test_list_files(drive_manager, test_profile):
    """Test listing files in folder."""
    folder_id = drive_manager.create_user_folder(test_profile)
    
    # Upload a test file
    drive_manager.upload_text(folder_id, "test_list.json", {"test": "data"})
    
    # List files
    files = drive_manager.list_files(folder_id)
    
    assert isinstance(files, list)
    assert len(files) > 0

def test_get_file_url(drive_manager):
    """Test generating file URL."""
    test_file_id = "test_file_id_123"
    url = drive_manager.get_file_url(test_file_id)
    
    assert "drive.google.com" in url
    assert test_file_id in url

# Instructions for running these tests:
"""
To run these integration tests:

1. Create a test Google account
2. Set up OAuth2 credentials in Google Cloud Console
3. Get an access token using the OAuth flow
4. Set environment variable:
   export GOOGLE_TEST_ACCESS_TOKEN="your_access_token_here"
5. Run tests:
   pytest backend/tests/test_drive_integration.py -v

Note: These tests will create folders and files in the test account's Drive.
Clean up manually after testing if needed.
"""
