"""Unit tests for transaction categorizer."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json

from src.categorizer import TransactionCategorizer
from src.parser import Transaction
from src.config import TxType, PaymentMode


@pytest.fixture
def temp_cache_file():
    """Create temporary cache file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        return f.name


@pytest.fixture
def categorizer(temp_cache_file):
    """Create categorizer instance with temp cache."""
    return TransactionCategorizer(api_key="test-key", cache_file=temp_cache_file)


@pytest.fixture
def sample_transaction():
    """Create sample transaction."""
    return Transaction(
        amount=2500.0,
        tx_type=TxType.DEBIT,
        mode=PaymentMode.UPI,
        merchant="SWIGGY",
        date=datetime.now(),
        raw_text="Rs.2500 debited for swiggy order"
    )


def test_rule_based_categorization(categorizer):
    """Test rule-based categorization."""
    # Test exact match
    assert categorizer._rule_based_category("swiggy") == "Food & Dining"
    assert categorizer._rule_based_category("SWIGGY") == "Food & Dining"

    # Test partial match
    assert categorizer._rule_based_category("SWIGGY BANGALORE") == "Food & Dining"
    assert categorizer._rule_based_category("BigBasket Store") == "Groceries"
    assert categorizer._rule_based_category("AMAZON.IN") == "Shopping"
    assert categorizer._rule_based_category("UBER TRIP") == "Transportation"

    # Test no match
    assert categorizer._rule_based_category("UNKNOWN MERCHANT") is None
    assert categorizer._rule_based_category(None) is None


def test_cache_key_generation(categorizer):
    """Test cache key generation."""
    assert categorizer._get_cache_key("SWIGGY") == "swiggy"
    assert categorizer._get_cache_key("Swiggy Bangalore") == "swiggy bangalore"
    assert categorizer._get_cache_key("A" * 60) == "a" * 50  # Truncated to 50
    assert categorizer._get_cache_key(None) == "unknown"


def test_categorize_with_rules(categorizer, sample_transaction):
    """Test categorization using rules (no LLM call)."""
    category = categorizer.categorize(sample_transaction)
    assert category == "Food & Dining"


def test_categorize_salary(categorizer):
    """Test salary categorization."""
    salary_tx = Transaction(
        amount=85000.0,
        tx_type=TxType.CREDIT,
        mode=PaymentMode.NEFT,
        merchant="SALARY-ACME CORP",
        date=datetime.now(),
        raw_text="Salary credited"
    )

    category = categorizer.categorize(salary_tx)
    assert category == "Salary"


def test_categorize_large_credit(categorizer):
    """Test large credit categorization (assumed salary)."""
    large_credit = Transaction(
        amount=75000.0,
        tx_type=TxType.CREDIT,
        mode=PaymentMode.NEFT,
        merchant="COMPANY XYZ",
        date=datetime.now(),
        raw_text="Credit received"
    )

    category = categorizer.categorize(large_credit)
    assert category == "Salary"


@patch('src.categorizer.Anthropic')
def test_categorize_with_llm(mock_anthropic, categorizer):
    """Test categorization with LLM fallback."""
    # Mock LLM response
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Shopping")]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    # Override the client
    categorizer.client = mock_anthropic.return_value

    unknown_tx = Transaction(
        amount=1500.0,
        tx_type=TxType.DEBIT,
        mode=PaymentMode.CARD,
        merchant="UNKNOWN STORE XYZ",
        date=datetime.now(),
        raw_text="Card payment"
    )

    category = categorizer.categorize(unknown_tx)
    assert category == "Shopping"

    # Verify LLM was called
    assert mock_anthropic.return_value.messages.create.called


@patch('src.categorizer.Anthropic')
def test_categorize_invalid_llm_response(mock_anthropic, categorizer):
    """Test handling of invalid LLM response."""
    # Mock LLM response with invalid category
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="InvalidCategory")]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    categorizer.client = mock_anthropic.return_value

    unknown_tx = Transaction(
        amount=1500.0,
        tx_type=TxType.DEBIT,
        mode=PaymentMode.CARD,
        merchant="UNKNOWN STORE",
        date=datetime.now(),
        raw_text="Card payment"
    )

    category = categorizer.categorize(unknown_tx)
    assert category == "Other"  # Should fallback to "Other"


@patch('src.categorizer.Anthropic')
def test_categorize_llm_error(mock_anthropic, categorizer):
    """Test handling of LLM API error."""
    # Mock LLM error
    mock_anthropic.return_value.messages.create.side_effect = Exception("API Error")
    categorizer.client = mock_anthropic.return_value

    unknown_tx = Transaction(
        amount=1500.0,
        tx_type=TxType.DEBIT,
        mode=PaymentMode.CARD,
        merchant="UNKNOWN STORE",
        date=datetime.now(),
        raw_text="Card payment"
    )

    category = categorizer.categorize(unknown_tx)
    assert category == "Other"  # Should fallback to "Other" on error


def test_cache_persistence(temp_cache_file):
    """Test cache loading and saving."""
    # Create categorizer and add to cache
    cat1 = TransactionCategorizer(api_key="test-key", cache_file=temp_cache_file)
    cat1.cache['test_merchant'] = 'Shopping'
    cat1._save_cache()

    # Create new categorizer and verify cache loaded
    cat2 = TransactionCategorizer(api_key="test-key", cache_file=temp_cache_file)
    assert cat2.cache['test_merchant'] == 'Shopping'


def test_categorize_batch(categorizer):
    """Test batch categorization."""
    transactions = [
        Transaction(
            amount=2500.0,
            tx_type=TxType.DEBIT,
            mode=PaymentMode.UPI,
            merchant="SWIGGY",
            date=datetime.now(),
            raw_text="Swiggy order"
        ),
        Transaction(
            amount=3500.0,
            tx_type=TxType.DEBIT,
            mode=PaymentMode.CARD,
            merchant="BIGBASKET",
            date=datetime.now(),
            raw_text="Grocery shopping"
        )
    ]

    categorized = categorizer.categorize_batch(transactions)

    assert len(categorized) == 2
    assert categorized[0]['category'] == "Food & Dining"
    assert categorized[1]['category'] == "Groceries"
    assert categorized[0]['amount'] == 2500.0
    assert categorized[1]['amount'] == 3500.0
