# Quick Reference Card

Essential commands and information for Gringotts.

---

## 🚀 Quick Start Commands

```bash
# 1. Push to GitHub
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/gringotts.git
git push -u origin main

# 2. Test locally
export EMAIL_ADDRESS="jrajrohit33@gmail.com"
export EMAIL_PASSWORD="qnxt nlip gdlu uhtk"
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_SERVICE_ACCOUNT='{"type":"service_account"...}'
export SPREADSHEET_ID="your-sheet-id"
python3 -m src.main

# 3. Test with pytest
pytest tests/ -v
```

---

## 📋 GitHub Secrets Required

Add these 5 secrets in Settings → Secrets and variables → Actions:

| Secret Name | Example Value | Where to Get |
|-------------|---------------|--------------|
| `EMAIL_ADDRESS` | jrajrohit33@gmail.com | Your Gmail |
| `EMAIL_PASSWORD` | qnxtnlipgdluuhtk | https://myaccount.google.com/apppasswords |
| `ANTHROPIC_API_KEY` | sk-ant-api03-xxx | https://console.anthropic.com/ |
| `GOOGLE_SERVICE_ACCOUNT` | {"type":"service_account"...} | Google Cloud Console |
| `SPREADSHEET_ID` | 1BxiMVs0XRA5nFMd... | Google Sheets URL |

---

## 🔑 Getting Credentials

### Gmail App Password
1. https://myaccount.google.com/security
2. Enable 2-Step Verification
3. https://myaccount.google.com/apppasswords
4. Generate for "Mail" → "Other"
5. Copy 16-character password (remove spaces)

### Anthropic API Key
1. https://console.anthropic.com/
2. Sign up / Log in
3. API Keys → Create Key
4. Copy key (starts with `sk-ant-`)

### Google Service Account
1. https://console.cloud.google.com/
2. Create project → Enable Google Sheets API
3. Credentials → Create Service Account
4. Keys → Add Key → JSON
5. Download JSON file
6. Copy entire JSON content

### Spreadsheet ID
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
                                          ^^^^^^^^^^^^^^^^^^^
```

---

## 🧪 Testing Commands

```bash
# Run all tests
pytest tests/

# Test with real emails (last 30 days)
python3 test_real_emails.py

# Dry run (no Google Sheets write)
python3 dry_run.py

# Validate configuration
python3 validate_config.py

# Test specific component
python3 test_parser.py
python3 test_categorizer.py
```

---

## 📊 Google Sheets Setup

1. Create new spreadsheet
2. Share with service account email: `gringotts-bot@PROJECT.iam.gserviceaccount.com`
3. Give "Editor" access
4. Copy Spreadsheet ID from URL
5. Sheets will be created automatically: "January 2026", "February 2026", etc.

---

## ⚙️ GitHub Actions

### Manual Trigger
1. Go to repository → Actions tab
2. Click "Gringotts Nightly Expense Tracker"
3. Click "Run workflow" → "Run workflow"

### View Logs
1. Actions tab → Click on workflow run
2. Click "fetch-and-process" job
3. Expand steps to see logs

### Download Failed Logs
1. Scroll to bottom of failed run
2. Look for "Artifacts" section
3. Download "gringotts-logs"

---

## 📁 Project Structure

```
gringotts/
├── src/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration & patterns
│   ├── email_fetcher.py     # IMAP client
│   ├── parser.py            # Transaction parser
│   ├── categorizer.py       # AI categorization
│   ├── deduplicator.py      # Remove duplicates
│   └── sheets.py            # Google Sheets writer
├── tests/
│   ├── test_parser.py       # Parser tests
│   ├── test_categorizer.py  # Categorizer tests
│   └── fixtures/            # Test data
├── .github/workflows/
│   └── nightly.yml          # GitHub Actions workflow
├── requirements.txt         # Python dependencies
└── README.md               # Documentation
```

---

## 🔧 Common Customizations

### Add New Bank
```python
# src/config.py
BANK_SENDERS = [
    'alerts@newbank.com',  # Add sender email
]

PATTERNS = {
    'newbank_debit': r'Rs\.?\s*(\d+)\s+debited.*?at\s+(.+)',  # Add pattern
}
```

### Add Merchant Rule
```python
# src/config.py
MERCHANT_RULES = {
    'your_gym': 'Healthcare',  # Lowercase, partial match
}
```

### Change Schedule
```yaml
# .github/workflows/nightly.yml
on:
  schedule:
    - cron: '30 0 * * *'  # 6:00 AM IST
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Missing required environment variable" | Check all 5 GitHub secrets are added |
| "IMAP connection failed" | Verify Gmail app password, remove spaces |
| "Failed to authenticate with Google Sheets" | Check service account JSON, verify sheet is shared |
| "No pattern matched" | Email not from supported bank, add pattern |
| Workflow doesn't run | Check cron syntax, wait 10 min (GitHub delay) |

---

## 📈 Monitoring

### Check Stats
- GitHub Actions usage: Settings → Billing → Actions
- Anthropic API usage: https://console.anthropic.com/
- Google Sheets API: https://console.cloud.google.com/apis/dashboard

### View Workflow History
- GitHub repo → Actions tab
- See all runs with ✅ success or ❌ failure

### Review Categorizations
- Open Google Sheet
- Check if categories are accurate
- Add rules in `MERCHANT_RULES` for frequent merchants

---

## 💰 Costs

| Service | Cost |
|---------|------|
| Anthropic API (Claude Haiku) | < $0.10/month |
| Google Sheets API | Free |
| GitHub Actions (private repo) | Free (2000 min/month) |
| **Total** | **~$0.10/month** |

---

## 📅 Schedule

- **Runs**: Daily at 2:30 AM IST (9:00 PM UTC)
- **Fetches**: Emails from last 25 hours
- **Processes**: Parses → Categorizes → Deduplicates → Writes to Sheets
- **Duration**: ~2-3 minutes per run

---

## 🔒 Security Checklist

- [x] Use GitHub Secrets (not hardcoded)
- [x] Repository is private
- [x] Gmail app password (not main password)
- [x] Service account (not personal OAuth)
- [x] `.env` file in `.gitignore`
- [x] Never commit credentials

---

## 📞 Quick Links

| Resource | URL |
|----------|-----|
| Gmail App Passwords | https://myaccount.google.com/apppasswords |
| Anthropic Console | https://console.anthropic.com/ |
| Google Cloud Console | https://console.cloud.google.com/ |
| Google Sheets | https://sheets.google.com/ |
| GitHub Actions | https://github.com/YOUR_USER/gringotts/actions |

---

## 🎯 Expected Output

```
============================================================
Gringotts - Automated Expense Tracker
============================================================
Loading configuration...
Fetching emails from the last 25 hours...
Found 15 emails
Parsing transactions...
Categorizing transactions...
Removing duplicates...
Writing to Google Sheets...
============================================================
Summary:
  Emails fetched: 15
  Transactions parsed: 12
  After deduplication: 11
  Written to Google Sheets: 11
============================================================
Transaction breakdown by category:
  Food & Dining: 3
  Shopping: 2
  Transportation: 1
  ...
Total Debits: ₹15,234.50
Total Credits: ₹85,000.00
Net: ₹69,765.50
============================================================
Gringotts run completed successfully!
```

---

## 🆘 Need Help?

1. Check `SETUP_GUIDE.md` for detailed setup
2. Check `LOCAL_TESTING.md` for testing locally
3. Check `CUSTOMIZATION.md` for customizations
4. Check `TESTING_REPORT.md` for test results
5. Review workflow logs in GitHub Actions
6. Validate config with `validate_config.py`

---

## ✅ Pre-Deployment Checklist

Before going live:

- [ ] All 5 GitHub secrets added
- [ ] Workflow file exists at `.github/workflows/nightly.yml`
- [ ] Google Sheet created and shared
- [ ] Tested manually in GitHub Actions
- [ ] Verified transactions in Google Sheet
- [ ] `.env` file deleted (if created locally)
- [ ] All code pushed to GitHub
