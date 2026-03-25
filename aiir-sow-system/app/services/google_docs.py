"""
Google Docs API Service Wrapper
Handles document operations: create from template, replace placeholders
"""

from typing import Dict, List, Any
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging
import re

logger = logging.getLogger(__name__)


class GoogleDocsService:
    """
    Google Docs API service wrapper

    Provides methods for:
    - Creating documents from templates
    - Replacing placeholders with actual values
    - Reading document content
    """

    def __init__(self, credentials_path_or_service, drive_service=None):
        """
        Initialize Google Docs service

        Args:
            credentials_path_or_service: Either a path to service account JSON file (str)
                                        or a pre-built Google Docs service object
            drive_service: Optional pre-built Google Drive service (needed for copying docs)
        """
        if isinstance(credentials_path_or_service, str):
            # Old behavior: build services from credentials file
            self.credentials_path = credentials_path_or_service
            self.docs_service = self._build_docs_service()
            self.drive_service = self._build_drive_service()
        else:
            # New behavior: use pre-built services (from GoogleServicesManager)
            self.docs_service = credentials_path_or_service
            self.drive_service = drive_service  # Must be provided when using service objects
            self.credentials_path = None

    def _build_docs_service(self):
        """Build Google Docs API service from credentials file"""
        SCOPES = ['https://www.googleapis.com/auth/documents']
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=SCOPES
        )
        return build('docs', 'v1', credentials=credentials)

    def _build_drive_service(self):
        """Build Google Drive API service from credentials file"""
        SCOPES = ['https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=SCOPES
        )
        return build('drive', 'v3', credentials=credentials)

    def create_from_template(
        self,
        template_id: str,
        new_title: str,
        destination_folder_id: str
    ) -> tuple[str, str]:
        """
        Create a new document from a template

        Args:
            template_id: Google Doc template ID
            new_title: Title for the new document
            destination_folder_id: Folder to place new document

        Returns:
            Tuple of (document_id, web_view_link)
        """
        try:
            # First, check if the template is a .docx file that needs conversion
            template_info = self.drive_service.files().get(
                fileId=template_id,
                fields='mimeType',
                supportsAllDrives=True
            ).execute()

            template_mime = template_info.get('mimeType')
            logger.info(f"Template MIME type: {template_mime}")

            # If it's a Word document, convert to Google Doc during copy
            copy_body = {
                'name': new_title,
                'parents': [destination_folder_id]
            }

            if template_mime == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                # Convert .docx to Google Doc format
                copy_body['mimeType'] = 'application/vnd.google-apps.document'
                logger.info("Converting .docx template to Google Doc format")

            # Copy the template (supports both Shared Drive and My Drive files)
            copied_file = self.drive_service.files().copy(
                fileId=template_id,
                body=copy_body,
                fields='id, webViewLink, mimeType',
                supportsAllDrives=True
            ).execute()

            doc_id = copied_file.get('id')
            web_link = copied_file.get('webViewLink')
            result_mime = copied_file.get('mimeType')

            logger.info(f"Created document '{new_title}' from template {template_id} (result MIME: {result_mime})")
            return doc_id, web_link

        except Exception as e:
            logger.error(f"Error creating document from template: {e}")
            raise

    def replace_placeholders(
        self,
        document_id: str,
        replacements: Dict[str, str]
    ) -> None:
        """
        Replace placeholders in document with actual values

        Placeholders should be in format {{PLACEHOLDER_NAME}}

        Args:
            document_id: Document to modify
            replacements: Dict mapping placeholder names to values
        """
        try:
            # Build requests for each replacement
            requests = []

            for placeholder, value in replacements.items():
                # Format placeholder as {{NAME}}
                placeholder_text = f"{{{{{placeholder}}}}}"

                requests.append({
                    'replaceAllText': {
                        'containsText': {
                            'text': placeholder_text,
                            'matchCase': False
                        },
                        'replaceText': str(value)
                    }
                })

            # Execute batch update
            if requests:
                self.docs_service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': requests}
                ).execute()

                logger.info(f"Replaced {len(replacements)} placeholders in document {document_id}")

        except Exception as e:
            logger.error(f"Error replacing placeholders: {e}")
            raise

    def get_document_content(self, document_id: str) -> str:
        """
        Get document content as plain text

        Args:
            document_id: Document ID

        Returns:
            Document content as string
        """
        try:
            doc = self.docs_service.documents().get(documentId=document_id).execute()

            content = []
            for element in doc.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for elem in element['paragraph'].get('elements', []):
                        if 'textRun' in elem:
                            content.append(elem['textRun'].get('content', ''))

            text = ''.join(content)
            logger.info(f"Retrieved document content, length: {len(text)} chars")
            return text

        except Exception as e:
            logger.error(f"Error getting document content: {e}")
            raise

    def export_as_pdf(self, document_id: str) -> bytes:
        """
        Export document as PDF

        Args:
            document_id: Document to export

        Returns:
            PDF content as bytes
        """
        try:
            pdf_content = self.drive_service.files().export(
                fileId=document_id,
                mimeType='application/pdf'
            ).execute()

            logger.info(f"Exported document {document_id} as PDF")
            return pdf_content

        except Exception as e:
            logger.error(f"Error exporting PDF: {e}")
            raise

    def insert_table(
        self,
        document_id: str,
        index: int,
        rows: int,
        columns: int,
        data: List[List[str]]
    ) -> None:
        """
        Insert a table at a specific location

        Args:
            document_id: Document to modify
            index: Character index where to insert table
            rows: Number of rows
            columns: Number of columns
            data: 2D list of cell values
        """
        try:
            requests = [
                {
                    'insertTable': {
                        'rows': rows,
                        'columns': columns,
                        'location': {
                            'index': index
                        }
                    }
                }
            ]

            # Execute insert
            result = self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            # TODO: Add requests to populate table cells with data
            # This would require calculating cell indices based on table structure

            logger.info(f"Inserted {rows}x{columns} table in document {document_id}")

        except Exception as e:
            logger.error(f"Error inserting table: {e}")
            raise
