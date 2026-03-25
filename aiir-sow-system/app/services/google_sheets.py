"""
Google Sheets API Service Wrapper
Handles spreadsheet operations: read, write, update rows
"""

from typing import List, Dict, Optional, Any
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """
    Google Sheets API service wrapper

    Provides methods for:
    - Reading ranges
    - Appending rows
    - Updating specific cells/ranges
    - Batch updates
    """

    def __init__(self, credentials_path_or_service):
        """
        Initialize Google Sheets service

        Args:
            credentials_path_or_service: Either a path to service account JSON file (str)
                                        or a pre-built Google Sheets service object
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
        """Build Google Sheets API service from credentials file"""
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=SCOPES
        )
        return build('sheets', 'v4', credentials=credentials)

    def read_range(
        self,
        spreadsheet_id: str,
        range_name: str
    ) -> List[List[Any]]:
        """
        Read values from a range

        Args:
            spreadsheet_id: Spreadsheet ID
            range_name: Range in A1 notation (e.g., 'Sheet1!A1:B10')

        Returns:
            2D list of cell values
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])
            logger.info(f"Read {len(values)} rows from {range_name}")
            return values

        except Exception as e:
            logger.error(f"Error reading range {range_name}: {e}")
            raise

    def append_row(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[Any]
    ) -> Dict:
        """
        Append a row to the end of a sheet

        NOTE: This method finds the next empty row in column A and writes there,
        rather than using the append API which can write to unexpected locations
        when there's data in columns beyond the target range.

        Args:
            spreadsheet_id: Spreadsheet ID
            range_name: Sheet name or range (e.g., 'Tracker' or 'Tracker!A:U')
            values: List of values to append

        Returns:
            Response dict with update info
        """
        try:
            # Extract sheet name from range (e.g., "Tracker" or "Tracker!A:U" -> "Tracker")
            sheet_name = range_name.split('!')[0]

            # Find the next empty row by checking column A
            last_row = self.get_last_row_number(spreadsheet_id, sheet_name, 'A')
            next_row = last_row + 1

            # Determine the column range to write to
            if '!' in range_name and ':' in range_name:
                # Extract column range from "Tracker!A:U" -> "A:U"
                col_range = range_name.split('!')[1]
                start_col = col_range.split(':')[0]
                end_col = col_range.split(':')[1]
                target_range = f"{sheet_name}!{start_col}{next_row}:{end_col}{next_row}"
            else:
                # No column range specified, write starting from A
                num_cols = len(values)
                end_col_idx = num_cols - 1
                end_col = self._column_index_to_letter(end_col_idx)
                target_range = f"{sheet_name}!A{next_row}:{end_col}{next_row}"

            # Use update instead of append to write to the exact location
            body = {
                'values': [values]
            }

            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=target_range,
                valueInputOption='RAW',
                body=body
            ).execute()

            logger.info(f"Appended row to {target_range}, {result.get('updatedCells')} cells updated")
            return result

        except Exception as e:
            logger.error(f"Error appending row to {range_name}: {e}")
            raise

    def _column_index_to_letter(self, index: int) -> str:
        """Convert column index (0-based) to letter (A, B, ..., Z, AA, AB, ...)"""
        result = ""
        index += 1  # Convert to 1-based
        while index > 0:
            index -= 1
            result = chr(65 + (index % 26)) + result
            index //= 26
        return result

    def update_range(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]]
    ) -> Dict:
        """
        Update a specific range with values

        Args:
            spreadsheet_id: Spreadsheet ID
            range_name: Range in A1 notation
            values: 2D list of values

        Returns:
            Response dict with update info
        """
        try:
            body = {
                'values': values
            }

            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()

            logger.info(f"Updated range {range_name}, {result.get('updatedCells')} cells updated")
            return result

        except Exception as e:
            logger.error(f"Error updating range {range_name}: {e}")
            raise

    def batch_update(
        self,
        spreadsheet_id: str,
        updates: List[Dict[str, Any]]
    ) -> Dict:
        """
        Perform multiple updates in a single request

        Args:
            spreadsheet_id: Spreadsheet ID
            updates: List of update dicts with 'range' and 'values' keys

        Returns:
            Response dict with batch update info
        """
        try:
            data = []
            for update in updates:
                data.append({
                    'range': update['range'],
                    'values': update['values']
                })

            body = {
                'valueInputOption': 'RAW',
                'data': data
            }

            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()

            logger.info(f"Batch updated {len(updates)} ranges")
            return result

        except Exception as e:
            logger.error(f"Error in batch update: {e}")
            raise

    def find_row_by_value(
        self,
        spreadsheet_id: str,
        range_name: str,
        search_column_index: int,
        search_value: str
    ) -> Optional[int]:
        """
        Find row number where a column contains a specific value

        Args:
            spreadsheet_id: Spreadsheet ID
            range_name: Range to search
            search_column_index: Column index to search (0-based)
            search_value: Value to find

        Returns:
            Row number (1-based) or None if not found
        """
        try:
            values = self.read_range(spreadsheet_id, range_name)

            for row_idx, row in enumerate(values, start=1):
                if len(row) > search_column_index:
                    if str(row[search_column_index]) == str(search_value):
                        logger.info(f"Found value '{search_value}' in row {row_idx}")
                        return row_idx

            logger.info(f"Value '{search_value}' not found in column {search_column_index}")
            return None

        except Exception as e:
            logger.error(f"Error finding row: {e}")
            raise

    def update_row_by_engagement_id(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        engagement_id: str,
        column_updates: Dict[str, Any]
    ) -> Dict:
        """
        Update specific columns in a row identified by engagement ID

        Args:
            spreadsheet_id: Spreadsheet ID
            sheet_name: Sheet name
            engagement_id: Engagement ID to find
            column_updates: Dict mapping column letters to values (e.g., {'G': 'url', 'H': 'url2'})

        Returns:
            Response dict
        """
        try:
            # Find row with this engagement ID (assuming column A)
            row_num = self.find_row_by_value(
                spreadsheet_id,
                f"{sheet_name}!A:A",
                0,
                engagement_id
            )

            if not row_num:
                raise ValueError(f"Engagement ID '{engagement_id}' not found")

            # Build batch update for each column
            updates = []
            for col_letter, value in column_updates.items():
                range_name = f"{sheet_name}!{col_letter}{row_num}"
                updates.append({
                    'range': range_name,
                    'values': [[value]]
                })

            return self.batch_update(spreadsheet_id, updates)

        except Exception as e:
            logger.error(f"Error updating row for engagement {engagement_id}: {e}")
            raise

    def get_last_row_number(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        column: str = 'A'
    ) -> int:
        """
        Get the last row number with data in a specific column

        Args:
            spreadsheet_id: Spreadsheet ID
            sheet_name: Sheet name
            column: Column letter (default 'A')

        Returns:
            Last row number (1-based)
        """
        try:
            range_name = f"{sheet_name}!{column}:{column}"
            values = self.read_range(spreadsheet_id, range_name)

            if not values:
                return 0

            return len(values)

        except Exception as e:
            logger.error(f"Error getting last row: {e}")
            raise
