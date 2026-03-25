"""
Google Services Manager
Centralized initialization for Google Drive, Sheets, Docs, Gmail APIs
Supports both JSON credentials (Railway) and file path (local)
"""

from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)


class GoogleServicesManager:
    """
    Manages all Google API service instances
    Handles credentials from either JSON string or file path
    """

    def __init__(self, config):
        """
        Initialize Google Services Manager

        Args:
            config: Config instance with get_google_credentials() method
        """
        self.config = config
        self._credentials = None
        self._drive_service = None
        self._sheets_service = None
        self._docs_service = None
        self._gmail_service = None

    def _get_credentials(self):
        """Get or create Google credentials"""
        if self._credentials is None:
            creds_dict = self.config.get_google_credentials()
            SCOPES = [
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/documents',
                'https://www.googleapis.com/auth/gmail.send'
            ]
            self._credentials = service_account.Credentials.from_service_account_info(
                creds_dict,
                scopes=SCOPES
            )
        return self._credentials

    def get_drive_service(self):
        """Get Google Drive API service"""
        if self._drive_service is None:
            credentials = self._get_credentials()
            self._drive_service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive service initialized")
        return self._drive_service

    def get_sheets_service(self):
        """Get Google Sheets API service"""
        if self._sheets_service is None:
            credentials = self._get_credentials()
            self._sheets_service = build('sheets', 'v4', credentials=credentials)
            logger.info("Google Sheets service initialized")
        return self._sheets_service

    def get_docs_service(self):
        """Get Google Docs API service"""
        if self._docs_service is None:
            credentials = self._get_credentials()
            self._docs_service = build('docs', 'v1', credentials=credentials)
            logger.info("Google Docs service initialized")
        return self._docs_service

    def get_gmail_service(self):
        """Get Gmail API service"""
        if self._gmail_service is None:
            credentials = self._get_credentials()
            self._gmail_service = build('gmail', 'v1', credentials=credentials)
            logger.info("Gmail service initialized")
        return self._gmail_service
