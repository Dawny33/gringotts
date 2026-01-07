"""Transaction deduplicator to remove duplicate transactions."""
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class TransactionDeduplicator:
    """Removes duplicate transactions based on amount, type, and date."""

    @staticmethod
    def _create_dedup_key(transaction: Dict) -> Tuple:
        """
        Create deduplication key for a transaction.

        Args:
            transaction: Transaction dictionary

        Returns:
            Tuple of (amount, tx_type, date_hour)
        """
        # Use hour-level precision for date to catch duplicates
        # within the same hour (e.g., email + SMS notifications)
        date_hour = transaction['date'].strftime('%Y-%m-%d-%H')

        return (
            transaction['amount'],
            transaction['tx_type'],
            date_hour
        )

    def deduplicate(self, transactions: List[Dict]) -> List[Dict]:
        """
        Remove duplicate transactions.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Deduplicated list of transactions
        """
        if not transactions:
            return []

        seen_keys = set()
        unique_transactions = []
        duplicate_count = 0

        for tx in transactions:
            key = self._create_dedup_key(tx)

            if key not in seen_keys:
                seen_keys.add(key)
                unique_transactions.append(tx)
            else:
                duplicate_count += 1
                logger.debug(f"Duplicate found: ₹{tx['amount']} {tx['tx_type']} on {tx['date']}")

        if duplicate_count > 0:
            logger.info(f"Removed {duplicate_count} duplicate transactions")
        else:
            logger.info("No duplicates found")

        return unique_transactions
