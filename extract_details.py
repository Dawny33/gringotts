"""Extract detailed information from specific failed emails."""
import sys
import os
import re
from email.header import decode_header

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.email_fetcher import EmailFetcher
from src.parser import TransactionParser

EMAIL_ADDRESS = "jrajrohit33@gmail.com"
EMAIL_PASSWORD = "qnxt nlip gdlu uhtk"

def decode_subject(subject):
    """Decode email subject from base64 if needed."""
    try:
        decoded_parts = decode_header(subject)
        decoded_subject = ''
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_subject += part.decode(encoding or 'utf-8')
            else:
                decoded_subject += part
        return decoded_subject
    except:
        return subject

def main():
    print("Fetching emails...")
    with EmailFetcher(EMAIL_ADDRESS, EMAIL_PASSWORD) as fetcher:
        emails = fetcher.fetch_emails(hours=720)

    parser = TransactionParser()
    failed = []

    for email in emails:
        tx = parser.parse(email.body, email.date)
        if not tx:
            failed.append(email)

    print(f"\nFound {len(failed)} failed emails\n")
    print("="*80)

    # Group by type
    for i, email in enumerate(failed[:10], 1):  # Show first 10
        decoded_subject = decode_subject(email.subject)
        print(f"\n--- Email #{i} ---")
        print(f"From: {email.sender}")
        print(f"Subject (decoded): {decoded_subject}")
        print(f"Date: {email.date}")
        print(f"\nBody (first 800 chars):")
        print(email.body[:800])
        print("\n" + "="*80)

if __name__ == '__main__':
    main()
