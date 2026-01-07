"""Examine the 2 potential transaction failures in detail."""
import sys
import os
from email.header import decode_header

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.email_fetcher import EmailFetcher
from src.parser import TransactionParser

EMAIL_ADDRESS = "jrajrohit33@gmail.com"
EMAIL_PASSWORD = "qnxt nlip gdlu uhtk"

def decode_subject(subject):
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
    with EmailFetcher(EMAIL_ADDRESS, EMAIL_PASSWORD) as fetcher:
        emails = fetcher.fetch_emails(hours=720)

    parser = TransactionParser()

    # Find the two failures
    axis_credit = None
    hdfc_update = None

    for email in emails:
        tx = parser.parse(email.body, email.date, email.subject)
        if not tx:
            decoded_subject = decode_subject(email.subject)
            if "1450" in decoded_subject and "credited" in decoded_subject:
                axis_credit = email
            elif "Account update" in decoded_subject and "HDFC" in decoded_subject:
                hdfc_update = email

    print("="*80)
    print("EMAIL #1: Axis Credit")
    print("="*80)
    if axis_credit:
        decoded_subject = decode_subject(axis_credit.subject)
        print(f"Subject: {decoded_subject}")
        print(f"Body (full):")
        print(axis_credit.body)
        print("\n" + "="*80)

        # Try to parse with debug
        result = parser.parse(axis_credit.body, axis_credit.date, axis_credit.subject)
        if result:
            print(f"✓ PARSED: ₹{result.amount} {result.tx_type.value}")
        else:
            print("✗ FAILED TO PARSE")

    print("\n\n" + "="*80)
    print("EMAIL #2: HDFC Account Update")
    print("="*80)
    if hdfc_update:
        decoded_subject = decode_subject(hdfc_update.subject)
        print(f"Subject: {decoded_subject}")
        print(f"Body (full):")
        print(hdfc_update.body)
        print("\n" + "="*80)

        # Try to parse
        result = parser.parse(hdfc_update.body, hdfc_update.date, hdfc_update.subject)
        if result:
            print(f"✓ PARSED: ₹{result.amount} {result.tx_type.value}")
        else:
            print("✗ FAILED TO PARSE")
            print("\nThis appears to be:")
            if "mobile" in hdfc_update.body.lower() or "app" in hdfc_update.body.lower():
                print("  → Mobile/App notification (NOT a transaction)")
            elif "secure" in hdfc_update.body.lower() or "tip" in hdfc_update.body.lower():
                print("  → Security tip/notification (NOT a transaction)")
            else:
                print("  → Unknown type - needs review")

if __name__ == '__main__':
    main()
