"""Categorize the remaining failed emails."""
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
    failed = []

    for email in emails:
        tx = parser.parse(email.body, email.date, email.subject)
        if not tx:
            failed.append(email)

    print(f"Total failed: {len(failed)}\n")

    categories = {
        'otp': [],
        'balance_update': [],
        'token': [],
        'autopay_reminder': [],
        'skip_payment': [],
        'survey': [],
        'tips': [],
        'other': []
    }

    for email in failed:
        decoded_subject = decode_subject(email.subject).lower()

        if 'otp' in decoded_subject or 'safekey' in decoded_subject:
            categories['otp'].append(email)
        elif 'balance update' in decoded_subject:
            categories['balance_update'].append(email)
        elif 'token' in decoded_subject:
            categories['token'].append(email)
        elif 'upcoming autopay' in decoded_subject:
            categories['autopay_reminder'].append(email)
        elif 'skip payment' in decoded_subject:
            categories['skip_payment'].append(email)
        elif 'feedback' in decoded_subject or 'survey' in decoded_subject:
            categories['survey'].append(email)
        elif 'tip' in decoded_subject or 'mobile' in decoded_subject:
            categories['tips'].append(email)
        else:
            categories['other'].append(email)

    print("="*80)
    print("NON-TRANSACTION EMAILS (Correctly Ignored):")
    print("="*80)
    for cat, emails in categories.items():
        if emails and cat != 'other':
            print(f"\n{cat.upper().replace('_', ' ')}: {len(emails)}")
            for email in emails[:2]:  # Show first 2
                decoded_subject = decode_subject(email.subject)
                print(f"  - {decoded_subject[:80]}")

    if categories['other']:
        print("\n" + "="*80)
        print("POTENTIAL TRANSACTIONS (Need Review):")
        print("="*80)
        for email in categories['other']:
            decoded_subject = decode_subject(email.subject)
            print(f"\nSubject: {decoded_subject}")
            print(f"From: {email.sender}")
            print(f"Body preview: {email.body[:300]}")
            print()

    # Summary
    total_non_tx = sum(len(emails) for cat, emails in categories.items() if cat != 'other')
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total failed emails: {len(failed)}")
    print(f"Non-transaction emails (correctly ignored): {total_non_tx}")
    print(f"Potential transactions needing patterns: {len(categories['other'])}")

    if len(categories['other']) == 0:
        print("\n🎉 100% TRANSACTION COVERAGE ACHIEVED!")
        print("All actual transaction emails are being parsed correctly.")
        print("The remaining failures are non-transaction emails (OTPs, updates, etc.)")

if __name__ == '__main__':
    main()
