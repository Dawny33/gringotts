"""Google Sheets writer for transaction data."""
import json
import logging
from typing import Dict, List
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class SheetsWriter:
    """Writes transactions to Google Sheets with monthly tabs."""

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    HEADER_ROW = ['Date', 'Amount', 'Credit/Debit', 'Mode', 'Category', 'Merchant']

    def __init__(self, credentials_json: str, spreadsheet_id: str):
        """
        Initialize Sheets writer.

        Args:
            credentials_json: JSON string of service account credentials
            spreadsheet_id: Google Sheet ID
        """
        self.spreadsheet_id = spreadsheet_id

        # Parse credentials
        try:
            creds_dict = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=self.SCOPES
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Successfully authenticated with Google Sheets")
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {e}")
            raise

    def _get_existing_sheets(self) -> List[str]:
        """
        Get list of existing sheet names.

        Returns:
            List of sheet names
        """
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()

            sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            return sheet_names
        except HttpError as e:
            logger.error(f"Error fetching spreadsheet metadata: {e}")
            raise

    def _create_sheet(self, sheet_name: str) -> None:
        """
        Create a new sheet with header row.

        Args:
            sheet_name: Name of the sheet to create
        """
        try:
            # Create sheet
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request_body
            ).execute()

            logger.info(f"Created sheet: {sheet_name}")

            # Add header row
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A1:F1",
                valueInputOption='RAW',
                body={'values': [self.HEADER_ROW]}
            ).execute()

            logger.info(f"Added header row to {sheet_name}")

        except HttpError as e:
            logger.error(f"Error creating sheet {sheet_name}: {e}")
            raise

    def _get_or_create_sheet(self, month_year: str) -> str:
        """
        Get or create sheet for a given month.

        Args:
            month_year: Month and year string (e.g., "January 2026")

        Returns:
            Sheet name
        """
        existing_sheets = self._get_existing_sheets()

        if month_year not in existing_sheets:
            logger.info(f"Sheet '{month_year}' doesn't exist, creating it")
            self._create_sheet(month_year)

        return month_year

    @staticmethod
    def _format_transaction_row(tx: Dict) -> List:
        """
        Format transaction as a row for Google Sheets.

        Args:
            tx: Transaction dictionary

        Returns:
            List of values for the row
        """
        return [
            tx['date'].strftime('%Y-%m-%d %H:%M'),  # Date
            tx['amount'],                            # Amount (INR)
            tx['tx_type'],                           # Credit/Debit
            tx['mode'],                              # UPI/Card/NEFT/Wallet
            tx['category'],                          # LLM-assigned category
            tx['merchant'] or 'Unknown'              # Merchant name
        ]

    def append_transactions(self, transactions: List[Dict]) -> int:
        """
        Append transactions to appropriate monthly sheets.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Number of transactions written
        """
        if not transactions:
            logger.info("No transactions to write")
            return 0

        # Group transactions by month
        transactions_by_month: Dict[str, List[Dict]] = {}
        for tx in transactions:
            month_year = tx['date'].strftime('%B %Y')  # e.g., "January 2026"
            if month_year not in transactions_by_month:
                transactions_by_month[month_year] = []
            transactions_by_month[month_year].append(tx)

        # Write to each monthly sheet
        total_written = 0
        for month_year, month_transactions in transactions_by_month.items():
            try:
                # Get or create sheet
                sheet_name = self._get_or_create_sheet(month_year)

                # Format rows
                rows = [self._format_transaction_row(tx) for tx in month_transactions]

                # Append to sheet
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_name}!A:F",
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': rows}
                ).execute()

                logger.info(f"Wrote {len(rows)} transactions to {sheet_name}")
                total_written += len(rows)

            except HttpError as e:
                logger.error(f"Error writing to sheet {month_year}: {e}")
                raise

        return total_written
