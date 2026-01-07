"""Unit tests for transaction parser."""
import json
import pytest
from datetime import datetime
from pathlib import Path

from src.parser import TransactionParser, Transaction
from src.config import TxType, PaymentMode


@pytest.fixture
def parser():
    """Create parser instance."""
    return TransactionParser()


@pytest.fixture
def sample_emails():
    """Load sample emails from fixtures."""
    fixture_path = Path(__file__).parent / 'fixtures' / 'sample_emails.json'
    with open(fixture_path, 'r') as f:
        return json.load(f)


def test_hdfc_upi_debit(parser, sample_emails):
    """Test HDFC UPI debit parsing."""
    test_data = sample_emails['hdfc_upi_debit']
    tx = parser.parse(test_data['body'], datetime.now())

    assert tx is not None
    assert tx.amount == test_data['expected']['amount']
    assert tx.tx_type.value == test_data['expected']['tx_type']
    assert tx.mode.value == test_data['expected']['mode']
    assert test_data['expected']['merchant'].split('@')[0] in tx.merchant.lower()


def test_hdfc_card_debit(parser, sample_emails):
    """Test HDFC card debit parsing."""
    test_data = sample_emails['hdfc_card_debit']
    tx = parser.parse(test_data['body'], datetime.now())

    assert tx is not None
    assert tx.amount == test_data['expected']['amount']
    assert tx.tx_type.value == test_data['expected']['tx_type']
    assert tx.mode.value == test_data['expected']['mode']
    assert 'STARBUCKS' in tx.merchant.upper()


def test_hdfc_credit(parser, sample_emails):
    """Test HDFC credit parsing."""
    test_data = sample_emails['hdfc_credit']
    tx = parser.parse(test_data['body'], datetime.now())

    assert tx is not None
    assert tx.amount == test_data['expected']['amount']
    assert tx.tx_type.value == test_data['expected']['tx_type']
    assert 'SALARY' in tx.merchant.upper() or 'ACME' in tx.merchant.upper()


def test_icici_debit(parser, sample_emails):
    """Test ICICI debit parsing."""
    test_data = sample_emails['icici_debit']
    tx = parser.parse(test_data['body'], datetime.now())

    assert tx is not None
    assert tx.amount == test_data['expected']['amount']
    assert tx.tx_type.value == test_data['expected']['tx_type']
    assert 'NETFLIX' in tx.merchant.upper()


def test_icici_credit(parser, sample_emails):
    """Test ICICI credit parsing."""
    test_data = sample_emails['icici_credit']
    tx = parser.parse(test_data['body'], datetime.now())

    assert tx is not None
    assert tx.amount == test_data['expected']['amount']
    assert tx.tx_type.value == test_data['expected']['tx_type']


def test_icici_card(parser, sample_emails):
    """Test ICICI card parsing."""
    test_data = sample_emails['icici_card']
    tx = parser.parse(test_data['body'], datetime.now())

    assert tx is not None
    assert tx.amount == test_data['expected']['amount']
    assert tx.tx_type.value == test_data['expected']['tx_type']
    assert tx.mode.value == test_data['expected']['mode']
    assert 'BIG BASKET' in tx.merchant.upper()


def test_axis_debit(parser, sample_emails):
    """Test Axis debit parsing."""
    test_data = sample_emails['axis_debit']
    tx = parser.parse(test_data['body'], datetime.now())

    assert tx is not None
    assert tx.amount == test_data['expected']['amount']
    assert tx.tx_type.value == test_data['expected']['tx_type']
    assert 'UBER' in tx.merchant.upper()


def test_indusind_upi(parser, sample_emails):
    """Test IndusInd UPI parsing."""
    test_data = sample_emails['indusind_upi']
    tx = parser.parse(test_data['body'], datetime.now())

    assert tx is not None
    assert tx.amount == test_data['expected']['amount']
    assert tx.tx_type.value == test_data['expected']['tx_type']
    assert tx.mode.value == test_data['expected']['mode']


def test_amex_spend(parser, sample_emails):
    """Test Amex spend parsing."""
    test_data = sample_emails['amex_spend']
    tx = parser.parse(test_data['body'], datetime.now())

    assert tx is not None
    assert tx.amount == test_data['expected']['amount']
    assert tx.tx_type.value == test_data['expected']['tx_type']
    assert tx.mode.value == test_data['expected']['mode']
    assert 'AMAZON' in tx.merchant.upper()


def test_phonepe(parser, sample_emails):
    """Test PhonePe parsing."""
    test_data = sample_emails['phonepe']
    tx = parser.parse(test_data['body'], datetime.now())

    assert tx is not None
    assert tx.amount == test_data['expected']['amount']
    assert tx.tx_type.value == test_data['expected']['tx_type']
    assert tx.mode.value == test_data['expected']['mode']


def test_large_amount_with_commas(parser, sample_emails):
    """Test parsing amounts with Indian comma notation."""
    test_data = sample_emails['large_amount_with_commas']
    tx = parser.parse(test_data['body'], datetime.now())

    assert tx is not None
    assert tx.amount == test_data['expected']['amount']
    assert tx.tx_type.value == test_data['expected']['tx_type']


def test_invalid_email(parser):
    """Test parsing invalid/non-transaction email."""
    invalid_text = "This is not a transaction email. Just a random message."
    tx = parser.parse(invalid_text, datetime.now())

    assert tx is None


def test_mode_inference(parser):
    """Test payment mode inference."""
    assert parser._infer_mode("UPI transaction to merchant@paytm") == PaymentMode.UPI
    assert parser._infer_mode("Card payment at POS terminal") == PaymentMode.CARD
    assert parser._infer_mode("NEFT transfer to account") == PaymentMode.NEFT
    assert parser._infer_mode("Paytm wallet payment") == PaymentMode.WALLET
    assert parser._infer_mode("Unknown payment method") == PaymentMode.UNKNOWN


def test_merchant_cleaning(parser):
    """Test merchant name cleaning."""
    assert parser._clean_merchant("MERCHANT NAME on 01-Jan-26") == "MERCHANT NAME"
    assert parser._clean_merchant("  MERCHANT  ") == "MERCHANT"
    assert parser._clean_merchant("123") is None
    assert parser._clean_merchant("") is None
    assert parser._clean_merchant(None) is None
