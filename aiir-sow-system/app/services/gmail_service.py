"""
Gmail API Service Wrapper
Handles email sending with attachments and HTML content
Supports both Service Account (with delegation) and OAuth2
"""

from typing import List, Optional
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import logging
import os

logger = logging.getLogger(__name__)


class GmailService:
    """
    Gmail API service wrapper

    Provides methods for:
    - Sending plain text emails
    - Sending HTML emails
    - Sending emails with attachments

    Supports two authentication modes:
    1. Service Account with domain-wide delegation (use_oauth2=False)
    2. OAuth2 user credentials (use_oauth2=True)
    """

    def __init__(
        self,
        credentials_path: str,
        send_as_email: str,
        use_oauth2: bool = False,
        oauth2_refresh_token: Optional[str] = None,
        oauth2_client_id: Optional[str] = None,
        oauth2_client_secret: Optional[str] = None
    ):
        """
        Initialize Gmail service

        Args:
            credentials_path: Path to service account JSON file (if not using OAuth2)
            send_as_email: Email address to send from
            use_oauth2: If True, use OAuth2 instead of service account
            oauth2_refresh_token: OAuth2 refresh token
            oauth2_client_id: OAuth2 client ID
            oauth2_client_secret: OAuth2 client secret
        """
        self.credentials_path = credentials_path
        self.send_as_email = send_as_email
        self.use_oauth2 = use_oauth2
        self.oauth2_refresh_token = oauth2_refresh_token
        self.oauth2_client_id = oauth2_client_id
        self.oauth2_client_secret = oauth2_client_secret
        self.service = self._build_service()

    def _build_service(self):
        """Build Gmail API service"""
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']

        if self.use_oauth2:
            # Use OAuth2 credentials
            logger.info("Using OAuth2 credentials for Gmail")

            if not all([self.oauth2_refresh_token, self.oauth2_client_id, self.oauth2_client_secret]):
                raise ValueError(
                    "OAuth2 mode requires refresh_token, client_id, and client_secret"
                )

            credentials = Credentials(
                token=None,  # Will be refreshed automatically
                refresh_token=self.oauth2_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.oauth2_client_id,
                client_secret=self.oauth2_client_secret,
                scopes=SCOPES
            )

            return build('gmail', 'v1', credentials=credentials)

        else:
            # Use service account with domain-wide delegation
            logger.info("Using Service Account with domain-wide delegation for Gmail")

            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=SCOPES
            )

            # Delegate to the user email
            delegated_credentials = credentials.with_subject(self.send_as_email)

            return build('gmail', 'v1', credentials=delegated_credentials)

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        is_html: bool = False,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> str:
        """
        Send an email

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            is_html: Whether body is HTML
            cc: CC recipients
            bcc: BCC recipients

        Returns:
            Message ID
        """
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['from'] = self.send_as_email
            message['subject'] = subject

            if cc:
                message['cc'] = ', '.join(cc)
            if bcc:
                message['bcc'] = ', '.join(bcc)

            # Add body
            mime_type = 'html' if is_html else 'plain'
            message.attach(MIMEText(body, mime_type))

            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            message_id = result.get('id')
            logger.info(f"Sent email to {to}, subject: '{subject}', message ID: {message_id}")
            return message_id

        except Exception as e:
            logger.error(f"Error sending email to {to}: {e}")
            raise

    def send_email_with_attachment(
        self,
        to: str,
        subject: str,
        body: str,
        attachment_filename: str,
        attachment_content: bytes,
        is_html: bool = False
    ) -> str:
        """
        Send an email with a file attachment

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            attachment_filename: Name of attachment file
            attachment_content: File content as bytes
            is_html: Whether body is HTML

        Returns:
            Message ID
        """
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['from'] = self.send_as_email
            message['subject'] = subject

            # Add body
            mime_type = 'html' if is_html else 'plain'
            message.attach(MIMEText(body, mime_type))

            # Add attachment
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(attachment_content)
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename={attachment_filename}'
            )
            message.attach(attachment)

            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            message_id = result.get('id')
            logger.info(f"Sent email with attachment to {to}, file: {attachment_filename}")
            return message_id

        except Exception as e:
            logger.error(f"Error sending email with attachment: {e}")
            raise
