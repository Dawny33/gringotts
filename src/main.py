"""Main orchestrator for Gringotts expense tracker."""
import logging
import sys
from datetime import datetime

from .config import Config
from .email_fetcher import EmailFetcher
from .parser import TransactionParser
from .categorizer import TransactionCategorizer
from .deduplicator import TransactionDeduplicator
from .sheets import SheetsWriter


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main entry point for Gringotts."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Gringotts - Automated Expense Tracker")
    logger.info("=" * 60)

    try:
        # 1. Load configuration
        logger.info("Loading configuration...")
        config = Config()

        # 2. Initialize components
        logger.info("Initializing components...")
        parser = TransactionParser()
        categorizer = TransactionCategorizer(config.anthropic_api_key)
        deduplicator = TransactionDeduplicator()
        sheets_writer = SheetsWriter(
            config.google_service_account,
            config.spreadsheet_id
        )

        # 3. Fetch emails
        logger.info("Fetching emails from the last 25 hours...")
        with EmailFetcher(
            config.email_address,
            config.email_password,
            config.imap_server,
            config.imap_port
        ) as fetcher:
            emails = fetcher.fetch_emails(hours=25)

        if not emails:
            logger.info("No emails found. Exiting.")
            return 0

        # 4. Parse transactions
        logger.info("Parsing transactions...")
        transactions = parser.parse_batch(emails)

        if not transactions:
            logger.info("No transactions parsed from emails. Exiting.")
            return 0

        # 5. Categorize transactions
        logger.info("Categorizing transactions...")
        categorized_transactions = categorizer.categorize_batch(transactions)

        # 6. Deduplicate
        logger.info("Removing duplicates...")
        unique_transactions = deduplicator.deduplicate(categorized_transactions)

        if not unique_transactions:
            logger.info("No unique transactions after deduplication. Exiting.")
            return 0

        # 7. Write to Google Sheets
        logger.info("Writing to Google Sheets...")
        written_count = sheets_writer.append_transactions(unique_transactions)

        # 8. Print summary
        logger.info("=" * 60)
        logger.info("Summary:")
        logger.info(f"  Emails fetched: {len(emails)}")
        logger.info(f"  Transactions parsed: {len(transactions)}")
        logger.info(f"  After deduplication: {len(unique_transactions)}")
        logger.info(f"  Written to Google Sheets: {written_count}")
        logger.info("=" * 60)

        # Print transaction breakdown by category
        category_counts = {}
        total_debit = 0
        total_credit = 0

        for tx in unique_transactions:
            category = tx['category']
            category_counts[category] = category_counts.get(category, 0) + 1

            if tx['tx_type'] == 'Debit':
                total_debit += tx['amount']
            else:
                total_credit += tx['amount']

        logger.info("Transaction breakdown by category:")
        for category, count in sorted(category_counts.items()):
            logger.info(f"  {category}: {count}")

        logger.info(f"\nTotal Debits: ₹{total_debit:,.2f}")
        logger.info(f"Total Credits: ₹{total_credit:,.2f}")
        logger.info(f"Net: ₹{total_credit - total_debit:,.2f}")
        logger.info("=" * 60)

        logger.info("Gringotts run completed successfully!")
        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
