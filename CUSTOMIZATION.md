# Customization Guide

Learn how to customize Gringotts for your specific needs.

---

## Adding New Banks

If you get transaction emails from a bank not yet supported, you can easily add it.

### Step 1: Add Bank Sender Email

Edit `src/config.py`:

```python
BANK_SENDERS = [
    # ... existing senders ...

    # Your new bank
    'alerts@yournewbank.com',
    'noreply@yournewbank.com',
]
```

### Step 2: Add Regex Patterns

Look at a sample email from your bank and create a pattern:

**Example email:**
```
Dear Customer,
INR 1500.00 was debited from your account XX1234
at MERCHANT NAME on 07-Jan-26.
```

Add pattern to `PATTERNS` in `src/config.py`:

```python
PATTERNS: Dict[str, str] = {
    # ... existing patterns ...

    # Your new bank
    'yournewbank_debit': r'(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+was debited.*?at\s+(.+?)\s+on',
    'yournewbank_credit': r'(?:INR|Rs\.?)\s*(\d+[\d,]*\.?\d*)\s+was credited',
}
```

### Step 3: Test the Pattern

```python
# test_new_pattern.py
from src.parser import TransactionParser
from datetime import datetime

parser = TransactionParser()

# Your actual email body
body = "INR 1500.00 was debited from your account XX1234 at MERCHANT NAME on 07-Jan-26."

result = parser.parse(body, datetime.now(), "")

if result:
    print(f"✅ Pattern works! Amount: ₹{result.amount}, Merchant: {result.merchant}")
else:
    print("❌ Pattern needs adjustment")
```

---

## Adding Custom Categories

### Option 1: Use Existing Categories

The default categories cover most expenses:
- Salary, Food & Dining, Groceries, Shopping, Utilities, Rent
- Transportation, Entertainment, Healthcare, Investment
- Transfer, EMI, Insurance, Other

### Option 2: Add New Categories

Edit `src/config.py`:

```python
CATEGORIES = [
    "Salary",
    "Food & Dining",
    "Groceries",
    "Shopping",
    "Utilities",
    "Rent",
    "Transportation",
    "Entertainment",
    "Healthcare",
    "Investment",
    "Transfer",
    "EMI",
    "Insurance",
    "Education",        # ← New category
    "Subscriptions",    # ← New category
    "Gifts",            # ← New category
    "Other"
]
```

**Note**: After adding categories, clear the cache file `.category_cache.json` to recategorize transactions.

---

## Adding Merchant Rules

To avoid LLM API calls for common merchants, add rules.

Edit `src/config.py`:

```python
MERCHANT_RULES: Dict[str, str] = {
    # ... existing rules ...

    # Your frequently used merchants
    'your_favorite_restaurant': 'Food & Dining',
    'your_gym': 'Healthcare',
    'your_salon': 'Healthcare',
    'coursera': 'Education',
    'udemy': 'Education',
}
```

**Tips:**
- Use lowercase for merchant names
- Use partial matches (e.g., 'amazon' matches 'AMAZON.IN', 'Amazon Pay', etc.)
- Add merchants you use frequently to save API costs

---

## Customizing the Schedule

The default schedule is 2:30 AM IST daily. To change it:

Edit `.github/workflows/nightly.yml`:

```yaml
on:
  schedule:
    # Run at different time (in UTC)
    # Examples:
    # 6:00 AM IST = 12:30 AM UTC = '30 0 * * *'
    # 10:00 PM IST = 4:30 PM UTC = '30 16 * * *'
    # Twice daily = use multiple cron entries:
    - cron: '0 3 * * *'   # 8:30 AM IST
    - cron: '0 15 * * *'  # 8:30 PM IST
```

**Cron format**: `minute hour day month weekday`
- `0 21 * * *` = Every day at 9:00 PM UTC (2:30 AM IST)
- `0 9 * * 1` = Every Monday at 9:00 AM UTC
- `*/6 * * * *` = Every 6 hours

**Note**: GitHub Actions may delay scheduled runs by up to 10 minutes during high load.

---

## Customizing Email Lookback Period

The default is 25 hours to ensure no emails are missed even with schedule delays.

### Change in Code

Edit `src/main.py`:

```python
# Fetch emails from last 48 hours instead of 25
emails = fetcher.fetch_emails(hours=48)
```

### Change via Environment Variable

Add to `src/config.py`:

```python
class Config:
    def __init__(self):
        # ... existing config ...
        self.lookback_hours = int(os.getenv('LOOKBACK_HOURS', '25'))
```

Then add GitHub Secret:
- Name: `LOOKBACK_HOURS`
- Value: `48` (or any number you want)

Update `.github/workflows/nightly.yml`:

```yaml
- name: Run Gringotts
  env:
    # ... existing env vars ...
    LOOKBACK_HOURS: ${{ secrets.LOOKBACK_HOURS }}
```

---

## Customizing Google Sheets Format

### Change Sheet Naming

Edit `src/sheets.py`:

```python
def _get_or_create_sheet(self, month_year: str) -> str:
    # Current: "January 2026"
    # Option 1: "2026-01"
    month_year = tx['date'].strftime('%Y-%m')

    # Option 2: "Jan 2026"
    month_year = tx['date'].strftime('%b %Y')

    # Option 3: "2026 - January"
    month_year = tx['date'].strftime('%Y - %B')
```

### Change Column Headers

Edit `src/sheets.py`:

```python
HEADER_ROW = [
    'Date',
    'Amount',
    'Credit/Debit',
    'Mode',
    'Category',
    'Merchant',
    'Notes'  # ← Add custom column
]
```

### Add Custom Columns

Edit `src/sheets.py` in `_format_transaction_row`:

```python
@staticmethod
def _format_transaction_row(tx: Dict) -> List:
    return [
        tx['date'].strftime('%Y-%m-%d %H:%M'),
        tx['amount'],
        tx['tx_type'],
        tx['mode'],
        tx['category'],
        tx['merchant'] or 'Unknown',
        tx.get('notes', '')  # ← Custom field
    ]
```

---

## Adding Notifications

### Option 1: Email Summary

Add to end of `src/main.py`:

```python
def send_email_summary(config, summary_data):
    """Send email summary of daily transactions."""
    import smtplib
    from email.mime.text import MimeText

    msg = MIMEText(f"""
    Daily Expense Summary

    Transactions: {summary_data['count']}
    Total Debits: ₹{summary_data['debits']:,.2f}
    Total Credits: ₹{summary_data['credits']:,.2f}
    Net: ₹{summary_data['net']:,.2f}
    """)

    msg['Subject'] = f"Gringotts Daily Summary - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = config.email_address
    msg['To'] = config.email_address

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(config.email_address, config.email_password)
        smtp.send_message(msg)

# Call it at the end of main()
send_email_summary(config, {
    'count': len(unique_transactions),
    'debits': total_debit,
    'credits': total_credit,
    'net': total_credit - total_debit
})
```

### Option 2: Telegram Notifications

```python
# Add to requirements.txt:
# python-telegram-bot>=20.0

def send_telegram_message(bot_token, chat_id, message):
    """Send Telegram notification."""
    import requests
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)

# Add to GitHub Secrets:
# TELEGRAM_BOT_TOKEN
# TELEGRAM_CHAT_ID

# Use in main.py:
send_telegram_message(
    os.getenv('TELEGRAM_BOT_TOKEN'),
    os.getenv('TELEGRAM_CHAT_ID'),
    f"📊 Daily Summary\n💳 {len(unique_transactions)} transactions\n💰 Net: ₹{total_credit - total_debit:,.2f}"
)
```

---

## Advanced Customizations

### 1. Multi-Account Support

Track multiple bank accounts in different sheets:

```python
# src/config.py
ACCOUNT_MAPPING = {
    'alerts@hdfcbank.net': 'HDFC Account',
    'alerts@axis.bank.in': 'Axis Account',
}

# src/sheets.py - modify to use account name
def append_transactions(self, transactions):
    # Group by account AND month
    by_account_month = {}

    for tx in transactions:
        account = self._get_account(tx)
        month = tx['date'].strftime('%B %Y')
        key = f"{account} - {month}"

        if key not in by_account_month:
            by_account_month[key] = []
        by_account_month[key].append(tx)

    # Write each account-month to separate sheet
    for sheet_name, txs in by_account_month.items():
        # ... write logic
```

### 2. Budget Alerts

Add budget checking:

```python
# src/config.py
MONTHLY_BUDGETS = {
    'Food & Dining': 15000,
    'Shopping': 10000,
    'Entertainment': 5000,
}

# src/main.py
def check_budgets(transactions, budgets):
    """Check if any category exceeded budget."""
    by_category = {}
    for tx in transactions:
        if tx['tx_type'] == 'Debit':
            cat = tx['category']
            by_category[cat] = by_category.get(cat, 0) + tx['amount']

    alerts = []
    for cat, spent in by_category.items():
        if cat in budgets and spent > budgets[cat]:
            alerts.append(f"⚠️ {cat}: ₹{spent:,.2f} / ₹{budgets[cat]:,.2f} (over budget!)")

    return alerts
```

### 3. Export to CSV

Add CSV export option:

```python
# src/exporter.py
import csv
from datetime import datetime

def export_to_csv(transactions, filename=None):
    """Export transactions to CSV."""
    if not filename:
        filename = f"transactions_{datetime.now().strftime('%Y%m%d')}.csv"

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'date', 'amount', 'type', 'mode', 'category', 'merchant'
        ])
        writer.writeheader()

        for tx in transactions:
            writer.writerow({
                'date': tx['date'].strftime('%Y-%m-%d %H:%M'),
                'amount': tx['amount'],
                'type': tx['tx_type'],
                'mode': tx['mode'],
                'category': tx['category'],
                'merchant': tx['merchant'] or ''
            })

    print(f"Exported to {filename}")
```

---

## Performance Optimizations

### 1. Reduce API Calls

The categorizer already caches results, but you can optimize further:

```python
# Increase cache hit rate by normalizing merchant names
def _get_cache_key(self, merchant: Optional[str]) -> str:
    if not merchant:
        return "unknown"

    # Remove common suffixes
    merchant = re.sub(r'\s+(pvt|ltd|limited|inc|llc|corp).*$', '', merchant, flags=re.IGNORECASE)
    # Remove special characters
    merchant = re.sub(r'[^a-z0-9\s]', '', merchant.lower())
    # Remove extra spaces
    merchant = re.sub(r'\s+', ' ', merchant).strip()

    return merchant[:50]
```

### 2. Batch Processing

Process emails in batches to reduce memory usage:

```python
# src/main.py
BATCH_SIZE = 50

for i in range(0, len(emails), BATCH_SIZE):
    batch = emails[i:i+BATCH_SIZE]
    transactions = parser.parse_batch(batch)
    categorized = categorizer.categorize_batch(transactions)
    # Process batch...
```

---

## Testing Customizations

Always test your customizations locally before deploying:

```bash
# 1. Make your changes
# 2. Run local tests
pytest tests/

# 3. Run dry run
python3 dry_run.py

# 4. Test with real data (write to test sheet)
# Set SPREADSHEET_ID to a test sheet
export SPREADSHEET_ID=your-test-sheet-id
python3 -m src.main

# 5. Verify in test Google Sheet
# 6. If all good, deploy to production
```

---

## Rollback Changes

If something breaks:

```bash
# Check git history
git log --oneline

# Rollback to previous version
git checkout <commit-hash> src/config.py

# Or reset to last working commit
git reset --hard <commit-hash>

# Force push to GitHub (if already pushed)
git push -f origin main
```

---

## Best Practices

1. **Test locally first** - Never deploy untested changes to production
2. **Keep backups** - Export Google Sheets data regularly
3. **Version control** - Commit changes with descriptive messages
4. **Document changes** - Add comments explaining custom patterns
5. **Monitor costs** - Check Anthropic API usage monthly
6. **Review accuracy** - Periodically verify categorizations are correct

---

## Getting Help

If you need help with customizations:

1. Check the code comments in `src/` files
2. Review existing patterns in `src/config.py`
3. Test incrementally (add one pattern at a time)
4. Check logs for error messages
5. Use the debugging scripts from `LOCAL_TESTING.md`
