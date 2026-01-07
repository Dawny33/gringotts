"""Comprehensive test script to verify 100% email parsing coverage."""
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.email_fetcher import EmailFetcher
from src.parser import TransactionParser
from src.config import BANK_SENDERS

# Test credentials
EMAIL_ADDRESS = "jrajrohit33@gmail.com"
EMAIL_PASSWORD = "qnxt nlip gdlu uhtk"

def main():
    print("=" * 80)
    print("GRINGOTTS - EXHAUSTIVE EMAIL TESTING")
    print("=" * 80)
    print()

    # Fetch emails
    print("Step 1: Fetching emails from the last 720 hours (30 days)...")
    print(f"Email: {EMAIL_ADDRESS}")
    print(f"Searching for senders: {len(BANK_SENDERS)} bank senders")
    print()

    try:
        with EmailFetcher(EMAIL_ADDRESS, EMAIL_PASSWORD) as fetcher:
            # Fetch last 30 days to get comprehensive coverage
            emails = fetcher.fetch_emails(hours=720)

        print(f"✓ Successfully fetched {len(emails)} emails")
        print()

        if not emails:
            print("⚠ No emails found. This could mean:")
            print("  - No transaction emails in the last 30 days")
            print("  - IMAP connection issue")
            print("  - Wrong credentials")
            return

        # Analyze emails
        print("=" * 80)
        print("Step 2: Analyzing fetched emails...")
        print("=" * 80)
        print()

        # Group by sender
        emails_by_sender = {}
        for email in emails:
            sender = email.sender
            if sender not in emails_by_sender:
                emails_by_sender[sender] = []
            emails_by_sender[sender].append(email)

        print(f"Emails grouped by {len(emails_by_sender)} unique senders:")
        for sender, sender_emails in sorted(emails_by_sender.items()):
            print(f"  {sender}: {len(sender_emails)} emails")
        print()

        # Parse all emails
        print("=" * 80)
        print("Step 3: Testing parser on all emails...")
        print("=" * 80)
        print()

        parser = TransactionParser()

        parsed_count = 0
        failed_count = 0
        failed_emails = []

        for i, email in enumerate(emails, 1):
            transaction = parser.parse(email.body, email.date, email.subject)

            if transaction:
                parsed_count += 1
                print(f"✓ [{i}/{len(emails)}] Parsed: ₹{transaction.amount:.2f} {transaction.tx_type.value} "
                      f"via {transaction.mode.value} - {transaction.merchant or 'Unknown'}")
            else:
                failed_count += 1
                failed_emails.append(email)
                print(f"✗ [{i}/{len(emails)}] FAILED to parse")
                print(f"    From: {email.sender}")
                print(f"    Subject: {email.subject[:80]}")
                print(f"    Body preview: {email.body[:150]}...")
                print()

        # Summary
        print()
        print("=" * 80)
        print("PARSING SUMMARY")
        print("=" * 80)
        print(f"Total emails fetched: {len(emails)}")
        print(f"Successfully parsed: {parsed_count}")
        print(f"Failed to parse: {failed_count}")
        print(f"Success rate: {(parsed_count/len(emails)*100):.1f}%")
        print()

        if failed_emails:
            print("=" * 80)
            print("FAILED EMAILS - NEED ATTENTION")
            print("=" * 80)
            print()

            for i, email in enumerate(failed_emails, 1):
                print(f"\n--- Failed Email #{i} ---")
                print(f"From: {email.sender}")
                print(f"Subject: {email.subject}")
                print(f"Date: {email.date}")
                print(f"Body:")
                print("-" * 80)
                print(email.body[:500])
                print("-" * 80)
                print()

        if failed_count == 0:
            print("🎉 SUCCESS! 100% parsing coverage achieved!")
        else:
            print(f"⚠ Need to add patterns for {failed_count} emails to achieve 100% coverage")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == '__main__':
    main()
