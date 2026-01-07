"""Transaction parser for extracting structured data from bank emails."""
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import logging

from .config import PATTERNS, TxType, PaymentMode

logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    """Structured transaction data."""
    amount: float
    tx_type: TxType
    mode: PaymentMode
    merchant: Optional[str]
    date: datetime
    raw_text: str  # First 200 chars for debugging


class TransactionParser:
    """Parses transaction details from email text."""

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize text for parsing.

        Args:
            text: Raw text

        Returns:
            Normalized text
        """
        # Remove commas from numbers
        text = re.sub(r'(\d),(\d)', r'\1\2', text)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def _infer_mode(text: str) -> PaymentMode:
        """
        Infer payment mode from text keywords.

        Args:
            text: Transaction text

        Returns:
            PaymentMode enum
        """
        text_lower = text.lower()

        if any(kw in text_lower for kw in ['upi', 'vpa', '@']):
            return PaymentMode.UPI
        elif any(kw in text_lower for kw in ['card', 'pos', 'atm']):
            return PaymentMode.CARD
        elif any(kw in text_lower for kw in ['neft', 'imps', 'rtgs']):
            return PaymentMode.NEFT
        elif any(kw in text_lower for kw in ['paytm', 'wallet']):
            return PaymentMode.WALLET

        return PaymentMode.UNKNOWN

    @staticmethod
    def _infer_tx_type(pattern_name: str, text: str) -> TxType:
        """
        Infer transaction type from pattern name and text.

        Args:
            pattern_name: Name of the matched pattern
            text: Transaction text

        Returns:
            TxType enum
        """
        pattern_lower = pattern_name.lower()
        text_lower = text.lower()

        # Check pattern name first
        if 'credit' in pattern_lower or 'payment' in pattern_lower:
            return TxType.CREDIT
        elif 'debit' in pattern_lower or 'spend' in pattern_lower:
            return TxType.DEBIT

        # Check text content
        if any(kw in text_lower for kw in ['credited', 'received', 'payment']):
            return TxType.CREDIT
        elif any(kw in text_lower for kw in ['debited', 'spent', 'paid', 'withdrawn']):
            return TxType.DEBIT

        # Default to debit (most transactions are debits)
        return TxType.DEBIT

    @staticmethod
    def _clean_merchant(merchant: Optional[str]) -> Optional[str]:
        """
        Clean and normalize merchant name.

        Args:
            merchant: Raw merchant name

        Returns:
            Cleaned merchant name or None
        """
        if not merchant:
            return None

        # Strip whitespace
        merchant = merchant.strip()

        # Remove common suffixes
        merchant = re.sub(r'\s+(on|at|via|using)\s+.*$', '', merchant, flags=re.IGNORECASE)

        # Remove extra whitespace
        merchant = re.sub(r'\s+', ' ', merchant).strip()

        # Remove if too short or just numbers
        if len(merchant) < 2 or merchant.isdigit():
            return None

        return merchant

    def parse(self, email_body: str, email_date: datetime) -> Optional[Transaction]:
        """
        Parse transaction from email body.

        Args:
            email_body: Email body text
            email_date: Email date

        Returns:
            Transaction object or None if no match
        """
        # Normalize text
        normalized_text = self._normalize_text(email_body)

        # Try each pattern
        for pattern_name, pattern in PATTERNS.items():
            try:
                match = re.search(pattern, normalized_text, re.IGNORECASE | re.DOTALL)
                if match:
                    # Extract amount (group 1)
                    amount_str = match.group(1)
                    amount = float(amount_str)

                    # Extract merchant (group 2 if exists)
                    merchant = None
                    if match.lastindex and match.lastindex >= 2:
                        merchant = self._clean_merchant(match.group(2))

                    # Infer transaction type
                    tx_type = self._infer_tx_type(pattern_name, normalized_text)

                    # Infer payment mode
                    mode = self._infer_mode(normalized_text)

                    # Create transaction
                    transaction = Transaction(
                        amount=amount,
                        tx_type=tx_type,
                        mode=mode,
                        merchant=merchant,
                        date=email_date,
                        raw_text=email_body[:200]  # First 200 chars for debugging
                    )

                    logger.debug(f"Matched pattern '{pattern_name}': {amount} {tx_type.value} via {mode.value}")
                    return transaction

            except Exception as e:
                logger.debug(f"Pattern '{pattern_name}' failed: {e}")
                continue

        # No pattern matched
        logger.warning(f"No pattern matched for email: {email_body[:100]}...")
        return None

    def parse_batch(self, emails: list) -> list[Transaction]:
        """
        Parse multiple emails.

        Args:
            emails: List of RawEmail objects

        Returns:
            List of Transaction objects
        """
        transactions = []
        for raw_email in emails:
            transaction = self.parse(raw_email.body, raw_email.date)
            if transaction:
                transactions.append(transaction)

        logger.info(f"Parsed {len(transactions)} transactions from {len(emails)} emails")
        return transactions
