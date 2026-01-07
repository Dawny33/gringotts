"""Debug the credit email failure."""
import sys
import os
from email.header import decode_header

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.email_fetcher import EmailFetcher
from src.parser import TransactionParser

EMAIL_ADDRESS = "jrajrohit33@gmail.com"
EMAIL_PASSWORD = "qnxt nlip gdlu uhtk"

def decode_subject(subject):
    """Decode email subject."""
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

    # Find the "credited" email
    for email in emails:
        decoded_subject = decode_subject(email.subject)
        if "450" in decoded_subject and "credited" in decoded_subject:
            print("Found the credit email!")
            print(f"Subject (raw): {email.subject}")
            print(f"Subject (decoded): {decoded_subject}")
            print(f"\nBody (first 1000 chars):")
            print(email.body[:1000])
            print("\n" + "="*80)

            # Try to parse
            result = parser.parse(email.body, email.date, email.subject)
            if result:
                print(f"✓ Parsed successfully: ₹{result.amount} {result.tx_type.value}")
            else:
                print("✗ Failed to parse")
                print("\nLet me try matching patterns manually...")

                from src.config import PATTERNS, SUBJECT_PATTERNS
                import re

                # Try subject patterns
                normalized_subject = parser._normalize_text(decoded_subject)
                print(f"\nNormalized subject: {normalized_subject}")

                for pattern_name, pattern in SUBJECT_PATTERNS.items():
                    match = re.search(pattern, normalized_subject, re.IGNORECASE)
                    if match:
                        print(f"✓ Matched subject pattern '{pattern_name}': {match.groups()}")
                    else:
                        print(f"✗ Pattern '{pattern_name}' didn't match")

                # Try body patterns
                normalized_body = parser._normalize_text(email.body)
                print(f"\nNormalized body (first 500): {normalized_body[:500]}")

                for pattern_name, pattern in PATTERNS.items():
                    if 'axis' in pattern_name and 'credit' in pattern_name:
                        match = re.search(pattern, normalized_body, re.IGNORECASE)
                        if match:
                            print(f"✓ Matched body pattern '{pattern_name}': {match.groups()}")
                        else:
                            print(f"✗ Pattern '{pattern_name}' didn't match")

            break

if __name__ == '__main__':
    main()
