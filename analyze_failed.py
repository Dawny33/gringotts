"""Analyze failed emails to understand what patterns are needed."""
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.email_fetcher import EmailFetcher
from src.parser import TransactionParser

EMAIL_ADDRESS = "jrajrohit33@gmail.com"
EMAIL_PASSWORD = "qnxt nlip gdlu uhtk"

def clean_html(text):
    """Remove HTML tags and extra whitespace."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&#8211;', '-')
    text = text.replace('&reg;', '')
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def categorize_failed_emails(emails):
    """Categorize failed emails by type."""
    parser = TransactionParser()

    categories = {
        'axis_cc_html': [],
        'indusind_payment': [],
        'hdfc_cc_debit': [],
        'hdfc_netbanking': [],
        'axis_credit': [],
        'axis_debit_alert': [],
        'axis_usd': [],
        'axis_autopay': [],
        'amex_balance': [],
        'amex_otp': [],
        'amex_token': [],
        'axis_autopay_reminder': [],
        'axis_skip_payment': [],
        'other': []
    }

    for email in emails:
        tx = parser.parse(email.body, email.date)
        if tx:
            continue  # Already parsed, skip

        subject = email.subject.lower()
        body = email.body.lower()

        # Categorize
        if 'spent on credit card' in subject and 'axis' in email.sender.lower():
            categories['axis_cc_html'].append(email)
        elif 'payment confirmation' in subject and 'indusind' in email.sender.lower():
            categories['indusind_payment'].append(email)
        elif 'debited via credit card' in subject and 'hdfc' in email.sender.lower():
            categories['hdfc_cc_debit'].append(email)
        elif 'account update' in subject and 'hdfc' in email.sender.lower():
            categories['hdfc_netbanking'].append(email)
        elif 'credited to your a/c' in subject and 'axis' in email.sender.lower():
            categories['axis_credit'].append(email)
        elif 'debit transaction alert' in subject and 'axis' in email.sender.lower():
            categories['axis_debit_alert'].append(email)
        elif 'usd' in subject and 'spent' in subject and 'axis' in email.sender.lower():
            categories['axis_usd'].append(email)
        elif 'autopay' in subject and 'activated' in subject:
            categories['axis_autopay'].append(email)
        elif 'balance update' in subject and 'amex' in email.sender.lower():
            categories['amex_balance'].append(email)
        elif 'otp' in subject.lower() or 'safekey' in subject.lower():
            categories['amex_otp'].append(email)
        elif 'token' in subject and 'amex' in email.sender.lower():
            categories['amex_token'].append(email)
        elif 'upcoming autopay' in subject:
            categories['axis_autopay_reminder'].append(email)
        elif 'skip payment' in subject:
            categories['axis_skip_payment'].append(email)
        else:
            categories['other'].append(email)

    return categories

def main():
    print("Fetching emails...")
    with EmailFetcher(EMAIL_ADDRESS, EMAIL_PASSWORD) as fetcher:
        emails = fetcher.fetch_emails(hours=720)

    print(f"Analyzing {len(emails)} emails...")
    categories = categorize_failed_emails(emails)

    # Print summary
    print("\n" + "="*80)
    print("CATEGORIZED FAILED EMAILS")
    print("="*80)

    # Transaction emails that need patterns
    print("\n🔴 TRANSACTION EMAILS NEEDING PATTERNS:")

    if categories['axis_cc_html']:
        print(f"\n1. Axis Bank Credit Card (HTML format): {len(categories['axis_cc_html'])} emails")
        email = categories['axis_cc_html'][0]
        print(f"   Subject: {email.subject}")
        cleaned = clean_html(email.body)
        print(f"   Cleaned body: {cleaned[:300]}...")

    if categories['indusind_payment']:
        print(f"\n2. IndusInd Payment Confirmation: {len(categories['indusind_payment'])} emails")
        email = categories['indusind_payment'][0]
        print(f"   Body: {email.body[:400]}...")

    if categories['hdfc_cc_debit']:
        print(f"\n3. HDFC Credit Card Debit: {len(categories['hdfc_cc_debit'])} emails")
        email = categories['hdfc_cc_debit'][0]
        print(f"   Subject: {email.subject}")
        cleaned = clean_html(email.body)
        print(f"   Cleaned body: {cleaned[:400]}...")

    if categories['hdfc_netbanking']:
        print(f"\n4. HDFC NetBanking Payment: {len(categories['hdfc_netbanking'])} emails")
        email = categories['hdfc_netbanking'][0]
        print(f"   Subject: {email.subject}")
        cleaned = clean_html(email.body)
        print(f"   Cleaned body: {cleaned[:400]}...")

    if categories['axis_credit']:
        print(f"\n5. Axis Bank Credit: {len(categories['axis_credit'])} emails")
        email = categories['axis_credit'][0]
        print(f"   Subject: {email.subject}")
        cleaned = clean_html(email.body)
        print(f"   Cleaned body: {cleaned[:300]}...")

    if categories['axis_debit_alert']:
        print(f"\n6. Axis Bank Debit Alert: {len(categories['axis_debit_alert'])} emails")
        email = categories['axis_debit_alert'][0]
        print(f"   Subject: {email.subject}")
        print(f"   Body: {email.body[:400]}...")

    if categories['axis_usd']:
        print(f"\n7. Axis Bank USD Transaction: {len(categories['axis_usd'])} emails")
        email = categories['axis_usd'][0]
        print(f"   Subject: {email.subject}")
        cleaned = clean_html(email.body)
        print(f"   Cleaned body: {cleaned[:300]}...")

    if categories['axis_autopay']:
        print(f"\n8. Axis Bank AutoPay Activation: {len(categories['axis_autopay'])} emails")
        email = categories['axis_autopay'][0]
        print(f"   Subject: {email.subject}")
        cleaned = clean_html(email.body)
        print(f"   Cleaned body: {cleaned[:400]}...")

    # Non-transaction emails to ignore
    print("\n\n🟡 NON-TRANSACTION EMAILS (can be ignored):")
    print(f"   - Axis AutoPay Reminders: {len(categories['axis_autopay_reminder'])}")
    print(f"   - Amex Balance Updates: {len(categories['amex_balance'])}")
    print(f"   - Amex OTP: {len(categories['amex_otp'])}")
    print(f"   - Amex Token: {len(categories['amex_token'])}")
    print(f"   - Axis Skip Payment: {len(categories['axis_skip_payment'])}")

    if categories['other']:
        print(f"\n❓ OTHER: {len(categories['other'])} emails")
        for email in categories['other']:
            print(f"   - Subject: {email.subject}")

if __name__ == '__main__':
    main()
