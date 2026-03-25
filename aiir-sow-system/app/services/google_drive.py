"""
Google Drive API Service Wrapper
Handles file operations: upload, download, list, move, delete
"""

import io
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)


class GoogleDriveService:
    """
    Google Drive API service wrapper

    Provides methods for:
    - Listing files in folders
    - Downloading files
    - Uploading files
    - Moving files between folders
    - Creating folders
    """

    def __init__(self, credentials_path_or_service):
        """
        Initialize Google Drive service

        Args:
            credentials_path_or_service: Either a path to service account JSON file (str)
                                        or a pre-built Google Drive service object
        """
        if isinstance(credentials_path_or_service, str):
            # Old behavior: build service from credentials file
            self.credentials_path = credentials_path_or_service
            self.service = self._build_service()
        else:
            # New behavior: use pre-built service (from GoogleServicesManager)
            self.service = credentials_path_or_service
            self.credentials_path = None

    def _build_service(self):
        """Build Google Drive API service from credentials file"""
        SCOPES = ['https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=SCOPES
        )
        return build('drive', 'v3', credentials=credentials)

    def list_files_in_folder(
        self,
        folder_id: str,
        mime_type: Optional[str] = None,
        order_by: str = 'createdTime desc'
    ) -> List[Dict]:
        """
        List files in a specific folder

        Args:
            folder_id: Google Drive folder ID
            mime_type: Filter by MIME type (e.g., 'text/plain')
            order_by: Sort order (default: newest first)

        Returns:
            List of file metadata dicts with id, name, mimeType, createdTime
        """
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            if mime_type:
                query += f" and mimeType='{mime_type}'"

            results = self.service.files().list(
                q=query,
                orderBy=order_by,
                fields="files(id, name, mimeType, createdTime, modifiedTime)",
                pageSize=100,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()

            files = results.get('files', [])
            logger.info(f"Found {len(files)} files in folder {folder_id}")
            return files

        except Exception as e:
            logger.error(f"Error listing files in folder {folder_id}: {e}")
            raise

    def download_file(self, file_id: str) -> str:
        """
        Download file content as text

        Args:
            file_id: Google Drive file ID

        Returns:
            File content as string
        """
        try:
            # For Google Docs, export as text
            # For other files, download directly
            file_metadata = self.service.files().get(
                fileId=file_id,
                supportsAllDrives=True
            ).execute()
            mime_type = file_metadata.get('mimeType', '')

            if 'google-apps' in mime_type:
                # Export Google Docs/Sheets/Slides
                if 'document' in mime_type:
                    export_mime = 'text/plain'
                elif 'spreadsheet' in mime_type:
                    export_mime = 'text/csv'
                else:
                    export_mime = 'application/pdf'

                request = self.service.files().export_media(
                    fileId=file_id,
                    mimeType=export_mime
                )
            else:
                # Download regular files
                request = self.service.files().get_media(fileId=file_id)

            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            content = fh.getvalue().decode('utf-8', errors='ignore')
            logger.info(f"Downloaded file {file_id}, size: {len(content)} chars")
            return content

        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            raise

    def upload_file(
        self,
        file_name: str,
        file_content: str,
        folder_id: str,
        mime_type: str = 'text/plain'
    ) -> str:
        """
        Upload a new file to Google Drive

        Args:
            file_name: Name for the new file
            file_content: Content as string
            folder_id: Destination folder ID
            mime_type: MIME type of file

        Returns:
            Created file ID
        """
        try:
            # Create file metadata
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }

            # Convert content to bytes
            content_bytes = file_content.encode('utf-8')
            fh = io.BytesIO(content_bytes)

            # Upload file
            media = MediaIoBaseUpload(fh, mimetype=mime_type, resumable=True)

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink',
                supportsAllDrives=True
            ).execute()

            file_id = file.get('id')
            web_link = file.get('webViewLink')

            logger.info(f"Uploaded file '{file_name}' to folder {folder_id}, ID: {file_id}")
            return file_id, web_link

        except Exception as e:
            logger.error(f"Error uploading file '{file_name}': {e}")
            raise

    def move_file(self, file_id: str, new_folder_id: str) -> None:
        """
        Move file to a different folder

        Args:
            file_id: File to move
            new_folder_id: Destination folder ID
        """
        try:
            # Get current parents
            file = self.service.files().get(
                fileId=file_id,
                fields='parents',
                supportsAllDrives=True
            ).execute()

            previous_parents = ','.join(file.get('parents', []))

            # Move file
            self.service.files().update(
                fileId=file_id,
                addParents=new_folder_id,
                removeParents=previous_parents,
                fields='id, parents',
                supportsAllDrives=True
            ).execute()

            logger.info(f"Moved file {file_id} to folder {new_folder_id}")

        except Exception as e:
            logger.error(f"Error moving file {file_id}: {e}")
            raise

    def create_folder(self, folder_name: str, parent_folder_id: str) -> str:
        """
        Create a new folder in Google Drive

        Args:
            folder_name: Name of new folder
            parent_folder_id: Parent folder ID

        Returns:
            Created folder ID
        """
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }

            folder = self.service.files().create(
                body=file_metadata,
                fields='id',
                supportsAllDrives=True
            ).execute()

            folder_id = folder.get('id')
            logger.info(f"Created folder '{folder_name}', ID: {folder_id}")
            return folder_id

        except Exception as e:
            logger.error(f"Error creating folder '{folder_name}': {e}")
            raise

    def get_file_metadata(self, file_id: str) -> Dict:
        """
        Get file metadata

        Args:
            file_id: File ID

        Returns:
            File metadata dict
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, createdTime, modifiedTime, parents, webViewLink',
                supportsAllDrives=True
            ).execute()

            return file

        except Exception as e:
            logger.error(f"Error getting metadata for file {file_id}: {e}")
            raise

    def delete_file(self, file_id: str) -> None:
        """
        Delete (trash) a file

        Args:
            file_id: File to delete
        """
        try:
            self.service.files().update(
                fileId=file_id,
                body={'trashed': True},
                supportsAllDrives=True
            ).execute()

            logger.info(f"Deleted (trashed) file {file_id}")

        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            raise
