"""Transaction categorizer using rules and LLM fallback."""
import json
import logging
from typing import Dict, Optional
from pathlib import Path

from anthropic import Anthropic

from .config import MERCHANT_RULES, CATEGORIES, LLM_MODEL, LLM_MAX_TOKENS, CACHE_FILE
from .parser import Transaction

logger = logging.getLogger(__name__)


class TransactionCategorizer:
    """Categorizes transactions using rules first, then LLM fallback."""

    def __init__(self, api_key: str, cache_file: str = CACHE_FILE):
        """
        Initialize categorizer.

        Args:
            api_key: Anthropic API key
            cache_file: Path to cache file
        """
        self.client = Anthropic(api_key=api_key)
        self.cache_file = Path(cache_file)
        self.cache: Dict[str, str] = self._load_cache()

    def _load_cache(self) -> Dict[str, str]:
        """
        Load category cache from file.

        Returns:
            Cache dictionary
        """
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                logger.info(f"Loaded {len(cache)} cached categories")
                return cache
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                return {}
        return {}

    def _save_cache(self) -> None:
        """Save category cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
            logger.debug("Cache saved")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _get_cache_key(self, merchant: Optional[str]) -> str:
        """
        Generate cache key from merchant name.

        Args:
            merchant: Merchant name

        Returns:
            Cache key
        """
        if not merchant:
            return "unknown"
        # Lowercase and truncate to 50 chars
        return merchant.lower()[:50]

    def _rule_based_category(self, merchant: Optional[str]) -> Optional[str]:
        """
        Attempt to categorize using rule-based matching.

        Args:
            merchant: Merchant name

        Returns:
            Category name or None
        """
        if not merchant:
            return None

        merchant_lower = merchant.lower()

        # Check exact matches and partial matches
        for key, category in MERCHANT_RULES.items():
            if key in merchant_lower:
                logger.debug(f"Rule-based match: '{merchant}' -> '{category}'")
                return category

        return None

    def _llm_category(self, transaction: Transaction) -> str:
        """
        Categorize using Claude Haiku.

        Args:
            transaction: Transaction object

        Returns:
            Category name
        """
        merchant = transaction.merchant or "Unknown"
        amount = transaction.amount
        tx_type = transaction.tx_type.value

        # Build prompt
        prompt = f"""Categorize this Indian transaction into exactly one category.

Categories: {', '.join(CATEGORIES)}

Transaction: "{merchant}", ₹{amount}, {tx_type}

Reply with just the category name."""

        try:
            logger.debug(f"Calling LLM for: {merchant}")
            response = self.client.messages.create(
                model=LLM_MODEL,
                max_tokens=LLM_MAX_TOKENS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract category from response
            category = response.content[0].text.strip()

            # Validate category
            if category not in CATEGORIES:
                logger.warning(f"LLM returned invalid category '{category}', using 'Other'")
                category = "Other"

            logger.debug(f"LLM categorized '{merchant}' as '{category}'")
            return category

        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return "Other"

    def categorize(self, transaction: Transaction) -> str:
        """
        Categorize a transaction.

        Args:
            transaction: Transaction object

        Returns:
            Category name
        """
        # Special handling for credits
        if transaction.tx_type.value == "Credit":
            # Check if it's a salary (large amount)
            if transaction.amount >= 50000:
                return "Salary"
            # Check if it's from a known source
            if transaction.merchant:
                merchant_lower = transaction.merchant.lower()
                if any(kw in merchant_lower for kw in ['salary', 'payroll', 'employer']):
                    return "Salary"
                elif any(kw in merchant_lower for kw in ['refund', 'return']):
                    # Use the merchant's category if known, else Other
                    rule_category = self._rule_based_category(transaction.merchant)
                    return rule_category if rule_category else "Other"

        # Try rule-based first
        category = self._rule_based_category(transaction.merchant)
        if category:
            return category

        # Check cache
        cache_key = self._get_cache_key(transaction.merchant)
        if cache_key in self.cache:
            logger.debug(f"Cache hit for '{transaction.merchant}'")
            return self.cache[cache_key]

        # Fallback to LLM
        category = self._llm_category(transaction)

        # Update cache
        self.cache[cache_key] = category
        self._save_cache()

        return category

    def categorize_batch(self, transactions: list[Transaction]) -> list[Dict]:
        """
        Categorize multiple transactions.

        Args:
            transactions: List of Transaction objects

        Returns:
            List of transaction dictionaries with categories
        """
        categorized = []
        for tx in transactions:
            category = self.categorize(tx)
            categorized.append({
                'date': tx.date,
                'amount': tx.amount,
                'tx_type': tx.tx_type.value,
                'mode': tx.mode.value,
                'merchant': tx.merchant,
                'category': category,
                'raw_text': tx.raw_text
            })

        logger.info(f"Categorized {len(categorized)} transactions")
        return categorized
