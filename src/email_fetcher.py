"""IMAP email fetcher for transaction emails."""
import imaplib
import email
from email.message import Message
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
import logging
import re

from .config import BANK_SENDERS

logger = logging.getLogger(__name__)


@dataclass
class RawEmail:
    """Structured representation of a raw email."""
    subject: str
    sender: str
    body: str
    date: datetime


class EmailFetcher:
    """Fetches transaction emails via IMAP."""

    def __init__(self, email_address: str, password: str, imap_server: str = 'imap.gmail.com', imap_port: int = 993):
        """
        Initialize email fetcher.

        Args:
            email_address: Email address to connect to
            password: Email password or app password
            imap_server: IMAP server address
            imap_port: IMAP server port
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.connection = None

    def connect(self) -> None:
        """Establish IMAP connection."""
        try:
            logger.info(f"Connecting to IMAP server {self.imap_server}:{self.imap_port}")
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.connection.login(self.email_address, self.password)
            logger.info("Successfully connected to IMAP server")
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during IMAP connection: {e}")
            raise

    def disconnect(self) -> None:
        """Close IMAP connection."""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                logger.info("Disconnected from IMAP server")
            except:
                pass

    def _build_search_query(self, since_date: datetime) -> str:
        """
        Build IMAP search query for multiple senders.

        Args:
            since_date: Fetch emails since this date

        Returns:
            IMAP search query string
        """
        # Format date for IMAP (DD-Mon-YYYY)
        date_str = since_date.strftime('%d-%b-%Y')

        # Build OR query for multiple senders
        # IMAP OR syntax: (OR (OR FROM "a" FROM "b") FROM "c")
        if not BANK_SENDERS:
            return f'SINCE {date_str}'

        if len(BANK_SENDERS) == 1:
            return f'(SINCE {date_str} FROM "{BANK_SENDERS[0]}")'

        # Build nested OR structure
        query = f'FROM "{BANK_SENDERS[0]}"'
        for sender in BANK_SENDERS[1:]:
            query = f'(OR {query} FROM "{sender}")'

        return f'(SINCE {date_str} {query})'

    def _extract_body(self, msg: Message) -> str:
        """
        Extract email body from message, handling multipart emails.

        Args:
            msg: Email message object

        Returns:
            Email body text
        """
        body = ""

        if msg.is_multipart():
            # Try to get plain text first, then HTML
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        continue

            # Fallback to HTML if no plain text found
            if not body:
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        try:
                            html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            # Strip HTML tags (basic)
                            body = re.sub(r'<[^>]+>', ' ', html_body)
                            body = re.sub(r'\s+', ' ', body).strip()
                            break
                        except:
                            continue
        else:
            # Non-multipart email
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())

        return body.strip()

    def fetch_emails(self, hours: int = 25) -> List[RawEmail]:
        """
        Fetch transaction emails from the last N hours.

        Args:
            hours: Number of hours to look back (default: 25)

        Returns:
            List of RawEmail objects
        """
        if not self.connection:
            raise RuntimeError("Not connected to IMAP server. Call connect() first.")

        try:
            # Select inbox
            self.connection.select('INBOX')

            # Calculate since date
            since_date = datetime.now() - timedelta(hours=hours)
            search_query = self._build_search_query(since_date)

            logger.info(f"Searching for emails since {since_date.strftime('%Y-%m-%d %H:%M')}")
            logger.debug(f"IMAP search query: {search_query}")

            # Search for emails
            status, messages = self.connection.search(None, search_query)

            if status != 'OK':
                logger.error(f"IMAP search failed: {status}")
                return []

            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} emails")

            if not email_ids:
                return []

            # Fetch emails
            raw_emails = []
            for email_id in email_ids:
                try:
                    status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        logger.warning(f"Failed to fetch email {email_id}")
                        continue

                    # Parse email
                    msg = email.message_from_bytes(msg_data[0][1])

                    # Extract fields
                    subject = msg.get('Subject', '')
                    sender = msg.get('From', '')
                    body = self._extract_body(msg)

                    # Parse date
                    date_str = msg.get('Date', '')
                    try:
                        date = email.utils.parsedate_to_datetime(date_str)
                    except:
                        date = datetime.now()

                    raw_emails.append(RawEmail(
                        subject=subject,
                        sender=sender,
                        body=body,
                        date=date
                    ))

                except Exception as e:
                    logger.warning(f"Error processing email {email_id}: {e}")
                    continue

            logger.info(f"Successfully fetched {len(raw_emails)} emails")
            return raw_emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            raise

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
