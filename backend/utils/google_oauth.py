"""
Google OAuth Handler
Manages OAuth2 flow for Google Sign-In and Drive access.
"""

import os
import logging
from typing import Dict, Any
from urllib.parse import urlencode
import requests

logger = logging.getLogger(__name__)

class GoogleOAuthHandler:
    """Handles Google OAuth2 authentication flow."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        self.auth_uri = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_uri = "https://oauth2.googleapis.com/token"
        self.userinfo_uri = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        # Scopes needed
        self.scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/drive.file"  # Access to files created by app
        ]
    
    def get_authorization_url(self) -> str:
        """
        Generate OAuth authorization URL.
        
        Returns:
            Authorization URL for user to visit
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "access_type": "offline",  # Get refresh token
            "prompt": "consent"  # Force consent screen to get refresh token
        }
        
        auth_url = f"{self.auth_uri}?{urlencode(params)}"
        logger.info(f"Generated auth URL with redirect: {self.redirect_uri}")
        return auth_url
    
    def exchange_code(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            {
                "access_token": "...",
                "refresh_token": "...",
                "expires_in": 3600,
                "token_type": "Bearer"
            }
        """
        try:
            data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }
            
            response = requests.post(self.token_uri, data=data, timeout=10)
            
            if response.status_code == 200:
                tokens = response.json()
                logger.info("Successfully exchanged code for tokens")
                return tokens
            else:
                error_msg = f"Token exchange failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            logger.error(f"Token exchange error: {str(e)}")
            return {"error": str(e)}
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New access token data
        """
        try:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
            
            response = requests.post(self.token_uri, data=data, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Refresh failed: {response.text}"}
                
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return {"error": str(e)}
    
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Get user profile information.
        
        Args:
            access_token: Valid access token
            
        Returns:
            {
                "id": "...",
                "email": "...",
                "name": "...",
                "picture": "..."
            }
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(self.userinfo_uri, headers=headers, timeout=10)
            
            if response.status_code == 200:
                profile = response.json()
                logger.info(f"Retrieved profile for user: {profile.get('email')}")
                return profile
            else:
                return {"error": f"Profile fetch failed: {response.text}"}
                
        except Exception as e:
            logger.error(f"Profile fetch error: {str(e)}")
            return {"error": str(e)}
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke an access or refresh token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if successful
        """
        try:
            revoke_uri = "https://oauth2.googleapis.com/revoke"
            params = {"token": token}
            response = requests.post(revoke_uri, params=params, timeout=10)
            
            if response.status_code == 200:
                logger.info("Token revoked successfully")
                return True
            else:
                logger.warning(f"Token revocation failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Token revocation error: {str(e)}")
            return False
