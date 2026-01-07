# Local Testing Guide

This guide helps you test Gringotts locally before deploying to GitHub Actions.

---

## Quick Local Test

### 1. Create `.env` File

Create a file named `.env` in the project root:

```bash
cd /Users/jalemrajrohit/Documents/VibeCoding/gringotts
touch .env
```

Add your credentials to `.env`:

```env
EMAIL_ADDRESS=jrajrohit33@gmail.com
EMAIL_PASSWORD=qnxt nlip gdlu uhtk
ANTHROPIC_API_KEY=your-api-key-here
GOOGLE_SERVICE_ACCOUNT={"type":"service_account","project_id":"...","private_key_id":"..."}
SPREADSHEET_ID=your-spreadsheet-id-here
```

**⚠️ IMPORTANT**: The `.env` file is already in `.gitignore` and will NOT be committed to git.

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Locally

```bash
# Load environment variables and run
export $(cat .env | xargs) && python3 -m src.main
```

Or create a simple test script:

```bash
# Create run_local.sh
cat > run_local.sh << 'EOF'
#!/bin/bash
set -a
source .env
set +a
python3 -m src.main
EOF

# Make it executable
chmod +x run_local.sh

# Run it
./run_local.sh
```

---

## Test Individual Components

### Test Email Fetching Only

```python
# test_email.py
from src.email_fetcher import EmailFetcher
from src.config import Config

config = Config()

with EmailFetcher(config.email_address, config.email_password) as fetcher:
    emails = fetcher.fetch_emails(hours=24)
    print(f"Fetched {len(emails)} emails")

    for email in emails[:5]:  # Show first 5
        print(f"\nFrom: {email.sender}")
        print(f"Subject: {email.subject}")
        print(f"Date: {email.date}")
```

Run: `export $(cat .env | xargs) && python3 test_email.py`

### Test Parser Only

```python
# test_parser.py
from src.parser import TransactionParser
from datetime import datetime

parser = TransactionParser()

# Test with sample email
sample_body = "Rs.2500.00 has been debited from A/c **1234 on 07-01-26. VPA swiggy@okaxis. Avl Bal: Rs.45000.00"
sample_subject = "Transaction Alert"

tx = parser.parse(sample_body, datetime.now(), sample_subject)

if tx:
    print(f"✅ Parsed: ₹{tx.amount} {tx.tx_type.value} via {tx.mode.value}")
    print(f"   Merchant: {tx.merchant}")
else:
    print("❌ Failed to parse")
```

Run: `python3 test_parser.py`

### Test Categorizer Only

```python
# test_categorizer.py
from src.categorizer import TransactionCategorizer
from src.parser import Transaction, TxType, PaymentMode
from src.config import Config
from datetime import datetime

config = Config()
categorizer = TransactionCategorizer(config.anthropic_api_key)

# Create test transaction
tx = Transaction(
    amount=2500.0,
    tx_type=TxType.DEBIT,
    mode=PaymentMode.UPI,
    merchant="SWIGGY",
    date=datetime.now(),
    raw_text="Test transaction"
)

category = categorizer.categorize(tx)
print(f"Category: {category}")
```

Run: `export $(cat .env | xargs) && python3 test_categorizer.py`

---

## Run Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_parser.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pip install pytest-cov
pytest tests/ --cov=src --cov-report=html
```

---

## Useful Testing Scripts

### 1. Dry Run (No Google Sheets Write)

Create `dry_run.py`:

```python
"""Dry run - test everything except writing to Google Sheets."""
import sys
from src.config import Config
from src.email_fetcher import EmailFetcher
from src.parser import TransactionParser
from src.categorizer import TransactionCategorizer
from src.deduplicator import TransactionDeduplicator

def main():
    print("=" * 60)
    print("DRY RUN - No data will be written to Google Sheets")
    print("=" * 60)

    config = Config()
    parser = TransactionParser()
    categorizer = TransactionCategorizer(config.anthropic_api_key)
    deduplicator = TransactionDeduplicator()

    # Fetch emails
    print("\n1. Fetching emails...")
    with EmailFetcher(config.email_address, config.email_password) as fetcher:
        emails = fetcher.fetch_emails(hours=25)
    print(f"   Found {len(emails)} emails")

    # Parse
    print("\n2. Parsing transactions...")
    transactions = parser.parse_batch(emails)
    print(f"   Parsed {len(transactions)} transactions")

    # Categorize
    print("\n3. Categorizing...")
    categorized = categorizer.categorize_batch(transactions)
    print(f"   Categorized {len(categorized)} transactions")

    # Deduplicate
    print("\n4. Deduplicating...")
    unique = deduplicator.deduplicate(categorized)
    print(f"   {len(unique)} unique transactions")

    # Show summary
    print("\n" + "=" * 60)
    print("SUMMARY (would be written to Google Sheets)")
    print("=" * 60)

    total_debit = sum(tx['amount'] for tx in unique if tx['tx_type'] == 'Debit')
    total_credit = sum(tx['amount'] for tx in unique if tx['tx_type'] == 'Credit')

    print(f"\nTotal Debits: ₹{total_debit:,.2f}")
    print(f"Total Credits: ₹{total_credit:,.2f}")
    print(f"Net: ₹{total_credit - total_debit:,.2f}")

    print("\nSample transactions (first 5):")
    for tx in unique[:5]:
        print(f"  {tx['date'].strftime('%Y-%m-%d')} | ₹{tx['amount']:,.2f} | "
              f"{tx['category']:20} | {tx['merchant'] or 'Unknown'}")

if __name__ == '__main__':
    main()
```

Run: `export $(cat .env | xargs) && python3 dry_run.py`

### 2. Test Specific Date Range

Create `test_date_range.py`:

```python
"""Test fetching emails from a specific date range."""
from src.email_fetcher import EmailFetcher
from src.config import Config

config = Config()

# Fetch last 7 days
with EmailFetcher(config.email_address, config.email_password) as fetcher:
    emails = fetcher.fetch_emails(hours=24*7)  # 7 days

print(f"Found {len(emails)} emails from last 7 days")

# Group by date
from collections import defaultdict
by_date = defaultdict(int)

for email in emails:
    date_str = email.date.strftime('%Y-%m-%d')
    by_date[date_str] += 1

print("\nEmails by date:")
for date in sorted(by_date.keys(), reverse=True):
    print(f"  {date}: {by_date[date]} emails")
```

Run: `export $(cat .env | xargs) && python3 test_date_range.py`

---

## Debugging Tips

### Enable Debug Logging

Create `debug_run.py`:

```python
"""Run with debug logging enabled."""
import logging
import sys

# Set up debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('gringotts_debug.log')
    ]
)

# Now import and run main
from src.main import main
main()
```

Run: `export $(cat .env | xargs) && python3 debug_run.py`

This will create a `gringotts_debug.log` file with detailed logs.

### Test with Sample Email

```python
# test_single_email.py
from src.parser import TransactionParser
from datetime import datetime

parser = TransactionParser()

# Your actual email body here
email_body = """
Paste your email body here
"""

email_subject = "Your email subject here"

result = parser.parse(email_body, datetime.now(), email_subject)

if result:
    print("✅ Successfully parsed!")
    print(f"   Amount: ₹{result.amount}")
    print(f"   Type: {result.tx_type.value}")
    print(f"   Mode: {result.mode.value}")
    print(f"   Merchant: {result.merchant}")
else:
    print("❌ Failed to parse")
    print("\nTrying to debug...")

    # Try matching against each pattern
    from src.config import PATTERNS
    import re

    normalized = parser._normalize_text(email_body)

    for name, pattern in PATTERNS.items():
        match = re.search(pattern, normalized, re.IGNORECASE | re.DOTALL)
        if match:
            print(f"✓ Pattern '{name}' matched: {match.groups()}")
```

---

## Validate Configuration

Create `validate_config.py`:

```python
"""Validate all configuration before running."""
import sys
from src.config import Config

print("Validating configuration...")
print("=" * 60)

try:
    config = Config()

    print("✅ EMAIL_ADDRESS:", config.email_address)
    print("✅ EMAIL_PASSWORD:", "•" * len(config.email_password), f"({len(config.email_password)} chars)")
    print("✅ ANTHROPIC_API_KEY:", config.anthropic_api_key[:20] + "..." if len(config.anthropic_api_key) > 20 else "✗ Too short")
    print("✅ SPREADSHEET_ID:", config.spreadsheet_id)

    # Test Google Service Account JSON
    import json
    sa_json = json.loads(config.google_service_account)
    print("✅ GOOGLE_SERVICE_ACCOUNT:")
    print(f"   - Type: {sa_json.get('type')}")
    print(f"   - Project: {sa_json.get('project_id')}")
    print(f"   - Email: {sa_json.get('client_email')}")

    print("\n" + "=" * 60)
    print("✅ All configuration valid!")

except ValueError as e:
    print(f"\n❌ Configuration error: {e}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"\n❌ GOOGLE_SERVICE_ACCOUNT is not valid JSON")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    sys.exit(1)
```

Run: `export $(cat .env | xargs) && python3 validate_config.py`

---

## Common Issues and Solutions

### Issue: ModuleNotFoundError

```bash
# Make sure you're in the right directory
cd /Users/jalemrajrohit/Documents/VibeCoding/gringotts

# Make sure dependencies are installed
pip install -r requirements.txt

# Make sure you're using the virtual environment
source venv/bin/activate
```

### Issue: Environment variables not loaded

```bash
# Check if .env file exists
cat .env

# Verify variables are exported
export $(cat .env | xargs)
echo $EMAIL_ADDRESS
```

### Issue: Import errors

```bash
# Run with -m flag (module mode)
python3 -m src.main

# Not: python3 src/main.py
```

---

## Clean Up Test Data

After testing, you may want to clean up:

```bash
# Remove debug logs
rm -f gringotts_debug.log

# Remove cache
rm -f .category_cache.json

# Remove test scripts
rm -f test_*.py dry_run.py validate_config.py

# Deactivate virtual environment
deactivate
```

---

## Next Steps

Once local testing is successful:

1. ✅ Verify all components work locally
2. ✅ Check Google Sheets for test data
3. ✅ Remove test data from Google Sheets (if needed)
4. ✅ Proceed with GitHub Actions setup
5. ✅ Delete `.env` file before pushing to GitHub (it's in .gitignore but be safe)

**Never commit `.env` file to git!**
