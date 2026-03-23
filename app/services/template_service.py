"""
Template Service - Handles duplication and population of Calculator and SOW templates
"""

from typing import Dict, Any, Tuple
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)


class TemplateService:
    """
    Service for managing document templates
    - Duplicate Calculator template (Google Sheets) for each client
    - Duplicate SOW template (Google Docs) for each client
    - Populate templates with engagement data
    """

    def __init__(self, credentials_path: str):
        """Initialize template service with Google credentials"""
        self.credentials_path = credentials_path
        self.drive_service = self._build_drive_service()
        self.sheets_service = self._build_sheets_service()
        self.docs_service = self._build_docs_service()

    def _build_drive_service(self):
        """Build Google Drive API service"""
        SCOPES = ['https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=SCOPES
        )
        return build('drive', 'v3', credentials=credentials)

    def _build_sheets_service(self):
        """Build Google Sheets API service"""
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=SCOPES
        )
        return build('sheets', 'v4', credentials=credentials)

    def _build_docs_service(self):
        """Build Google Docs API service"""
        SCOPES = ['https://www.googleapis.com/auth/documents']
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=SCOPES
        )
        return build('docs', 'v1', credentials=credentials)

    def duplicate_calculator_template(
        self,
        template_id: str,
        client_name: str,
        engagement_id: str,
        destination_folder_id: str
    ) -> Tuple[str, str]:
        """
        Duplicate calculator template for a specific client

        Args:
            template_id: Source template file ID
            client_name: Client company name
            engagement_id: Unique engagement ID
            destination_folder_id: Folder to place the duplicated file

        Returns:
            Tuple of (file_id, web_view_link)
        """
        try:
            new_title = f"{client_name} - Pricing Calculator - {engagement_id}"

            # Duplicate the file (with Shared Drive support)
            # Also convert Excel to Google Sheets format
            copied_file = self.drive_service.files().copy(
                fileId=template_id,
                body={
                    'name': new_title,
                    'parents': [destination_folder_id],
                    'mimeType': 'application/vnd.google-apps.spreadsheet'  # Convert to Google Sheets
                },
                fields='id, webViewLink, mimeType',
                supportsAllDrives=True  # Enable Shared Drive support
            ).execute()

            file_id = copied_file.get('id')
            web_link = copied_file.get('webViewLink')
            mime_type = copied_file.get('mimeType')

            logger.info(f"Duplicated calculator template: {new_title}")
            logger.info(f"  File ID: {file_id}")
            logger.info(f"  MIME Type: {mime_type}")
            logger.info(f"  URL: {web_link}")

            return file_id, web_link

        except Exception as e:
            logger.error(f"Error duplicating calculator template: {e}")
            raise

    def populate_calculator(
        self,
        file_id: str,
        pricing_data: Dict[str, Any]
    ) -> None:
        """
        Populate the duplicated calculator with actual pricing data including reduced hours

        Args:
            file_id: The duplicated calculator file ID (Google Sheets)
            pricing_data: Dictionary with pricing information
                - bill_rate: hourly rate
                - program_tier: ROADMAP, IGNITE, or ASCENT
                - session_hours: SessionHours object with actual hours (after reductions)
                - num_participants: number of people (default 1)
        """
        try:
            updates = []
            tier = pricing_data.get('program_tier', 'IGNITE')

            # Set the coaching bill rate
            if 'bill_rate' in pricing_data:
                updates.append({
                    'range': 'Coaching Calculator!B15',
                    'values': [[f"${pricing_data['bill_rate']}"]]
                })
                logger.info(f"Setting bill rate to: ${pricing_data['bill_rate']}/hour")

            # Update session hours for the specific tier (IGNITE rows 37-46)
            if 'session_hours' in pricing_data and tier == 'IGNITE':
                sh = pricing_data['session_hours']

                # Map session hours to IGNITE section cells (column B)
                updates.append({
                    'range': 'Coaching Calculator!B39',  # Developmental History
                    'values': [[sh.developmental_history_hours]]
                })
                updates.append({
                    'range': 'Coaching Calculator!B40',  # 360 Interviews
                    'values': [[sh.threesixty_interview_hours]]
                })
                updates.append({
                    'range': 'Coaching Calculator!B41',  # Assessment Feedback
                    'values': [[sh.assessment_feedback_hours]]
                })
                updates.append({
                    'range': 'Coaching Calculator!B44',  # Implementation Sessions
                    'values': [[sh.implementation_sessions]]
                })
                updates.append({
                    'range': 'Coaching Calculator!B45',  # Stakeholder 3 - Mid-Point
                    'values': [[sh.stakeholder_sessions_hours / 4]]  # Divide by 4 stakeholders
                })

                # Update Coaching Zone months (Row 37, Column E)
                updates.append({
                    'range': 'Coaching Calculator!E37',  # Coaching Zone months
                    'values': [[sh.coaching_zone_months]]
                })

                logger.info(f"Setting IGNITE session hours: Impl={sh.implementation_sessions}, 360={sh.threesixty_interview_hours}, DevHist={sh.developmental_history_hours}, Stakeholder={sh.stakeholder_sessions_hours}, CoachingZone={sh.coaching_zone_months}mo")

            # Set number of participants (if more than 1)
            if 'num_participants' in pricing_data and pricing_data['num_participants'] > 1:
                num_participants = pricing_data['num_participants']

                if tier == 'ROADMAP':
                    updates.append({
                        'range': 'Coaching Calculator!E31',
                        'values': [[num_participants]]
                    })
                elif tier == 'IGNITE':
                    updates.append({
                        'range': 'Coaching Calculator!E49',
                        'values': [[num_participants]]
                    })
                elif tier == 'ASCENT':
                    updates.append({
                        'range': 'Coaching Calculator!E67',
                        'values': [[num_participants]]
                    })

                logger.info(f"Setting {num_participants} participants for {tier}")

            # Batch update all cells
            if updates:
                data = [{'range': u['range'], 'values': u['values']} for u in updates]
                body = {
                    'valueInputOption': 'USER_ENTERED',
                    'data': data
                }

                self.sheets_service.spreadsheets().values().batchUpdate(
                    spreadsheetId=file_id,
                    body=body
                ).execute()

                logger.info(f"Calculator populated with {len(updates)} updates including actual session hours")
            else:
                logger.warning("No updates to make to calculator")

        except Exception as e:
            logger.error(f"Error populating calculator: {e}")
            raise

    def read_calculator_total_price(
        self,
        file_id: str,
        tier: str = 'IGNITE'
    ) -> float:
        """
        Read the calculated total price from the Calculator sheet

        This makes the Calculator the single source of truth for pricing.
        After populating inputs (bill rate, session hours), this method reads
        the final calculated price that includes all formulas, PM fee, etc.

        Args:
            file_id: The calculator file ID (Google Sheets)
            tier: Program tier (ROADMAP, IGNITE, ASCENT) to know which cell to read

        Returns:
            Total calculated price as float
        """
        try:
            # Map tier to the correct "Total Services Cost" cell
            tier_to_cell = {
                'ROADMAP': 'Coaching Calculator!B34',    # ROADMAP Total Services Cost
                'IGNITE': 'Coaching Calculator!B50',     # IGNITE Total Services Cost
                'ASCENT': 'Coaching Calculator!B68',     # ASCENT Total Services Cost
            }

            cell = tier_to_cell.get(tier, 'Coaching Calculator!B50')  # Default to IGNITE

            # Read the calculated total
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=file_id,
                range=cell
            ).execute()

            value = result.get('values', [['']])[0][0]

            # Parse the value (could be "$9,356" or "9356" or "$9,356.00")
            if isinstance(value, str):
                # Remove $ and commas, convert to float
                clean_value = value.replace('$', '').replace(',', '').strip()
                total_price = float(clean_value)
            else:
                total_price = float(value)

            logger.info(f"Read calculated price from Calculator {cell}: ${total_price:,.2f}")
            return total_price

        except Exception as e:
            logger.error(f"Error reading calculator total price: {e}")
            raise

    def duplicate_sow_template(
        self,
        template_id: str,
        client_name: str,
        engagement_id: str,
        destination_folder_id: str
    ) -> Tuple[str, str]:
        """
        Duplicate SOW template for a specific client

        Args:
            template_id: Source SOW template document ID
            client_name: Client company name
            engagement_id: Unique engagement ID
            destination_folder_id: Folder to place the duplicated document

        Returns:
            Tuple of (document_id, web_view_link)
        """
        try:
            new_title = f"{client_name} - Statement of Work - {engagement_id}"

            # Duplicate the document (with Shared Drive support)
            # Also convert Word to Google Docs format
            copied_file = self.drive_service.files().copy(
                fileId=template_id,
                body={
                    'name': new_title,
                    'parents': [destination_folder_id],
                    'mimeType': 'application/vnd.google-apps.document'  # Convert to Google Docs
                },
                fields='id, webViewLink, mimeType',
                supportsAllDrives=True  # Enable Shared Drive support
            ).execute()

            doc_id = copied_file.get('id')
            web_link = copied_file.get('webViewLink')
            mime_type = copied_file.get('mimeType')

            logger.info(f"Duplicated SOW template: {new_title}")
            logger.info(f"  Document ID: {doc_id}")
            logger.info(f"  MIME Type: {mime_type}")
            logger.info(f"  URL: {web_link}")

            return doc_id, web_link

        except Exception as e:
            logger.error(f"Error duplicating SOW template: {e}")
            raise

    def populate_sow(
        self,
        document_id: str,
        sow_data: Dict[str, str]
    ) -> None:
        """
        Populate the duplicated SOW with engagement data

        Args:
            document_id: The duplicated SOW document ID
            sow_data: Dictionary with placeholder replacements
                     Keys should match {{PLACEHOLDER}} in template
        """
        try:
            # Build replacement requests
            requests = []

            for placeholder, value in sow_data.items():
                # Replace {{PLACEHOLDER}} with actual value
                requests.append({
                    'replaceAllText': {
                        'containsText': {
                            'text': f'{{{{{placeholder}}}}}',
                            'matchCase': False
                        },
                        'replaceText': str(value) if value else ''
                    }
                })

            if requests:
                # Execute batch update
                self.docs_service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': requests}
                ).execute()

                logger.info(f"Populated SOW with {len(requests)} replacements")

        except Exception as e:
            logger.error(f"Error populating SOW: {e}")
            raise
