"""Configuration and constants for Gringotts expense tracker."""
import os
from enum import Enum
from typing import Dict, List


class TxType(Enum):
    """Transaction type enum."""
    CREDIT = "Credit"
    DEBIT = "Debit"


class PaymentMode(Enum):
    """Payment mode enum."""
    UPI = "UPI"
    CARD = "Card"
    NEFT = "NEFT"
    WALLET = "Wallet"
    UNKNOWN = "Unknown"


# Bank senders to filter for transaction emails
BANK_SENDERS = [
    # === USER'S PRIMARY BANKS ===
    # HDFC
    'alerts@hdfcbank.net',

    # ICICI Credit Cards
    'credit_cards@icicibank.com',

    # Axis Bank
    'alerts@axis.bank.in',

    # IndusInd Bank
    'transactionalert@indusind.com',

    # American Express
    'AmericanExpress@welcome.americanexpress.com',

    # === ADDITIONAL COMMON SENDERS (for completeness) ===
    # HDFC additional
    'alerts.cards@hdfcbank.net',

    # ICICI additional
    'noreply@icicibank.com',
    'transaction@icicibank.com',

    # Axis additional
    'alerts@axisbank.com',
    'noreply@axisbank.co.in',

    # UPI Apps
    'no-reply@phonepe.com',
    'noreply@paytm.com',

    # GPay (uses bank backends)
    'noreply@okaxis.com',
    'noreply@okhdfcbank.com',
    'noreply@okicici.com',
]

# Spending categories
CATEGORIES = [
    "Salary",
    "Food & Dining",
    "Groceries",
    "Shopping",
    "Utilities",
    "Rent",
    "Transportation",
    "Entertainment",
    "Healthcare",
    "Investment",
    "Transfer",
    "EMI",
    "Insurance",
    "Other"
]

# Rule-based merchant to category mapping
MERCHANT_RULES: Dict[str, str] = {
    # Food & Dining
    'swiggy': 'Food & Dining',
    'zomato': 'Food & Dining',
    'dominos': 'Food & Dining',
    'mcdonalds': 'Food & Dining',
    'starbucks': 'Food & Dining',
    'kfc': 'Food & Dining',

    # Groceries
    'bigbasket': 'Groceries',
    'blinkit': 'Groceries',
    'zepto': 'Groceries',
    'dmart': 'Groceries',
    'instamart': 'Groceries',
    'jiomart': 'Groceries',

    # Shopping
    'amazon': 'Shopping',
    'flipkart': 'Shopping',
    'myntra': 'Shopping',
    'ajio': 'Shopping',
    'nykaa': 'Shopping',

    # Transportation
    'uber': 'Transportation',
    'ola': 'Transportation',
    'rapido': 'Transportation',
    'irctc': 'Transportation',
    'makemytrip': 'Transportation',

    # Entertainment
    'netflix': 'Entertainment',
    'spotify': 'Entertainment',
    'hotstar': 'Entertainment',
    'bookmyshow': 'Entertainment',
    'pvr': 'Entertainment',

    # Utilities
    'bescom': 'Utilities',
    'jio': 'Utilities',
    'airtel': 'Utilities',
    'vodafone': 'Utilities',
}

# Regex patterns for transaction parsing
PATTERNS: Dict[str, str] = {
    # HDFC
    'hdfc_debit_upi': r'Rs\.?\s*(\d+[\d,]*\.?\d*)\s+(?:has been |)debited.*?(?:VPA|UPI)[:\s]+(\S+)',
    'hdfc_debit_card': r'Rs\.?\s*(\d+[\d,]*\.?\d*)\s+(?:has been |)(?:spent|debited).*?(?:card|Card).*?(?:at|for)\s+(.+?)(?:\s+on|\.|$)',
    'hdfc_credit': r'Rs\.?\s*(\d+[\d,]*\.?\d*)\s+(?:has been |)credited.*?(?:from|by)\s+(.+?)(?:\s+on|\.|$)',
    'hdfc_cc_debit': r'Rs\.?\s*(\d+[\d,]*\.?\d*)\s+(?:is |)debited from your HDFC Bank Credit Card.*?towards\s+(.+?)(?:\s+on|\.|$)',
    'hdfc_netbanking': r'(?:payment of|NetBanking for payment of)\s+Rs\.?\s*(\d+[\d,]*\.?\d*)\s+from\s+A/c\s+\S+\s+to\s+(.+?)(?:\s+Not|$)',
    'hdfc_neft': r'Rs\.?\s*(\d+[\d,]*\.?\d*)\s+has been deducted from your HDFC Bank account.*?for a transfer to payee\s+(.+?)\s+via\s+(?:NEFT|IMPS|RTGS)',

    # ICICI (including credit cards)
    'icici_debit': r'debited\s+(?:for\s+)?(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*).*?(?:Info[:\s]+)?(.+?)(?:\.|$)',
    'icici_credit': r'credited\s+(?:with\s+)?(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)',
    'icici_card': r'(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+(?:spent|charged|was used).*?(?:at|on)\s+(.+?)(?:\s+on|\.|$)',

    # Axis Bank
    'axis_debit': r'(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+(?:debited|spent).*?(?:at|to|for)\s+(.+?)(?:\s+on|\.|$)',
    'axis_credit': r'(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+(?:credited|received)',
    'axis_credit_subject': r'(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+was credited to your A/c',
    'axis_credit_body': r'Amount Credited:\s*(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)',
    'axis_cc_html_body': r'Transaction Amount:\s*(?:INR|USD)\s*&nbsp;\s*(\d+[\d,]*\.?\d*)\s*Merchant Name:\s*(.+?)\s+Axis Bank',
    'axis_debit_alert': r'A/c no\.\s+\S+\s+has been debited with\s+(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)',
    'axis_autopay': r'AutoPay transaction.*?Transaction Amount:\s*(USD|INR)\s*(\d+[\d,]*\.?\d*)\s*Merchant Name:\s*(.+?)\s+(?:Axis|Auto)',

    # IndusInd Bank
    'indusind_debit': r'(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+(?:has been |)(?:debited|spent|withdrawn).*?(?:at|to|for|Info[:\s]+)\s*(.+?)(?:\s+on|\.|Avl|$)',
    'indusind_credit': r'(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+(?:has been |)credited.*?(?:from|by)\s+(.+?)(?:\s+on|\.|$)',
    'indusind_upi': r'(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+.*?(?:UPI|VPA)[:\s]+(\S+)',
    'indusind_payment': r'Payment of INR\s+(\d+[\d,]*\.?\d*)\s+towards your IndusInd Bank Credit Card',

    # American Express (India - INR only)
    'amex_spend': r'(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+(?:was |has been |)(?:spent|charged|used).*?(?:at|on)\s+(.+?)(?:\s+on|\.|$)',
    'amex_payment': r'(?:payment|Payment)\s+(?:of\s+)?(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+(?:received|credited)',
    'amex_transaction': r'(?:Card|card)\s+.*?(?:ending|xxxx)\s*\d+.*?(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+(?:at|on)\s+(.+?)(?:\.|$)',

    # Generic UPI
    'upi_debit': r'(?:paid|sent|debited)\s+(?:Rs\.?|₹)\s*(\d+[\d,]*\.?\d*)\s+(?:to|for)\s+(.+?)(?:\s+via|\s+using|\s+on|$)',
    'upi_credit': r'(?:received|credited)\s+(?:Rs\.?|₹)\s*(\d+[\d,]*\.?\d*)\s+from\s+(.+?)(?:\s+via|\s+on|$)',

    # PhonePe
    'phonepe': r'(?:Paid|Sent)\s+Rs\.?\s*(\d+[\d,]*\.?\d*)\s+to\s+(.+?)\s+(?:on|via)',

    # Paytm
    'paytm': r'Paytm.*?(?:Paid|Sent)\s+Rs\.?\s*(\d+[\d,]*\.?\d*)\s+to\s+(.+)',
}

# Subject-only patterns (for emails with HTML bodies)
SUBJECT_PATTERNS: Dict[str, str] = {
    'axis_cc_subject_inr': r'(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+spent on credit card',
    'axis_cc_subject_usd': r'(USD)\s+(\d+[\d,]*\.?\d*)\s+spent on credit card',
}

# IMAP configuration
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

# LLM configuration
LLM_MODEL = 'claude-haiku-4-5-20251001'
LLM_MAX_TOKENS = 20

# Cache file for categorization
CACHE_FILE = '.category_cache.json'


class Config:
    """Configuration loaded from environment variables."""

    def __init__(self):
        """Load configuration from environment variables with validation."""
        self.email_address = self._get_required_env('EMAIL_ADDRESS')
        self.email_password = self._get_required_env('EMAIL_PASSWORD')
        self.anthropic_api_key = self._get_required_env('ANTHROPIC_API_KEY')
        self.google_service_account = self._get_required_env('GOOGLE_SERVICE_ACCOUNT')
        self.spreadsheet_id = self._get_required_env('SPREADSHEET_ID')

        # Optional configuration
        self.imap_server = os.getenv('IMAP_SERVER', IMAP_SERVER)
        self.imap_port = int(os.getenv('IMAP_PORT', str(IMAP_PORT)))

    @staticmethod
    def _get_required_env(key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Missing required environment variable: {key}")
        return value
