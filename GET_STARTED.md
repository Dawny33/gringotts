# Get Started with Gringotts

**Complete this guide in 15 minutes to start automated expense tracking!**

---

## What is Gringotts?

Gringotts automatically tracks your expenses by:
1. Reading transaction emails from your Gmail (IMAP)
2. Extracting transaction details (amount, merchant, date)
3. Categorizing them with AI (Claude Haiku)
4. Writing everything to a Google Sheet

**Cost:** ~₹10/month ($0.10)
**Time to setup:** 15 minutes
**Maintenance:** Zero - runs automatically every night

---

## Quick Setup (5 Steps)

### Step 1: Credentials (5 min)

Get these 3 things:

**A. Gmail App Password**
1. Go to https://myaccount.google.com/apppasswords
2. Create for "Mail" → "Other (Gringotts)"
3. Copy 16-character password → Remove spaces
4. Save it: `qnxt nlip gdlu uhtk` → `qnxtnlipgdluuhtk`

**B. Anthropic API Key**
1. Go to https://console.anthropic.com/
2. Sign up → API Keys → Create Key
3. Copy key (starts with `sk-ant-`)
4. Save it

**C. Google Service Account**
1. Go to https://console.cloud.google.com/
2. New Project → "Gringotts"
3. Enable "Google Sheets API"
4. Credentials → Create Service Account → "gringotts-bot"
5. Keys → Add Key → JSON → Download
6. Save the JSON file

### Step 2: Google Sheet (2 min)

1. Go to https://sheets.google.com/
2. Create new spreadsheet → Name it "Gringotts"
3. Share with service account email from JSON: `gringotts-bot@...iam.gserviceaccount.com`
4. Give "Editor" access
5. Copy Spreadsheet ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit
   ```

### Step 3: GitHub (3 min)

1. Create repo: https://github.com/new
   - Name: `gringotts`
   - Visibility: **Private**
2. Push code:
   ```bash
   cd /Users/jalemrajrohit/Documents/VibeCoding/gringotts
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/gringotts.git
   git push -u origin main
   ```

### Step 4: GitHub Secrets (3 min)

Go to: Repo → Settings → Secrets and variables → Actions

Add these 5 secrets:

| Secret Name | Value | Notes |
|-------------|-------|-------|
| `EMAIL_ADDRESS` | jrajrohit33@gmail.com | Your Gmail |
| `EMAIL_PASSWORD` | qnxtnlipgdluuhtk | App password (no spaces!) |
| `ANTHROPIC_API_KEY` | sk-ant-xxx | Your Claude key |
| `GOOGLE_SERVICE_ACCOUNT` | {"type":"service_account"...} | Entire JSON |
| `SPREADSHEET_ID` | 1BxiMVs0XRA5n... | From Sheet URL |

### Step 5: Test (2 min)

1. Go to Actions tab
2. Click "Gringotts Nightly Expense Tracker"
3. Click "Run workflow" → "Run workflow"
4. Wait ~2 minutes
5. See ✅ green checkmark
6. Open Google Sheet → See transactions!

---

## That's It!

🎉 **You're done!** Gringotts will now run every night at 2:30 AM IST.

### What Happens Automatically:

```
2:30 AM IST every day:
├─ Fetch emails from last 25 hours
├─ Parse transactions (amount, merchant, date)
├─ Categorize with AI
├─ Remove duplicates
└─ Write to Google Sheet (monthly tabs)
```

---

## Next Steps

### Verify It's Working

**Tomorrow morning:**
1. Check GitHub Actions tab → Should see automated run ✅
2. Check Google Sheet → Should see new transactions

**If something fails:**
- Check [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) → Troubleshooting

### Customize (Optional)

- **Add your banks**: Edit `src/config.py` → `BANK_SENDERS`
- **Add merchants**: Edit `src/config.py` → `MERCHANT_RULES`
- **Change schedule**: Edit `.github/workflows/nightly.yml` → `cron`

See [CUSTOMIZATION.md](CUSTOMIZATION.md) for details.

---

## Documentation Index

| Guide | Purpose | Time |
|-------|---------|------|
| **[GET_STARTED.md](GET_STARTED.md)** | You are here! Quick 15-min setup | 15 min |
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | Detailed step-by-step setup | 30 min |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | Commands, links, troubleshooting | 2 min |
| **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** | Pre-launch checklist | 10 min |
| **[LOCAL_TESTING.md](LOCAL_TESTING.md)** | Test locally before deploying | Optional |
| **[CUSTOMIZATION.md](CUSTOMIZATION.md)** | Add banks, patterns, features | Optional |
| **[TESTING_REPORT.md](TESTING_REPORT.md)** | See test coverage report | Optional |

---

## Support

### Common Issues

**"Missing required environment variable"**
→ Check secret names are EXACT (case-sensitive)

**"IMAP connection failed"**
→ Remove spaces from app password: `qnxt nlip gdlu uhtk` → `qnxtnlipgdluuhtk`

**"Failed to authenticate with Google Sheets"**
→ Verify sheet is shared with service account email

**"No emails found"**
→ This is OK if you had no transactions in last 25 hours

### Need More Help?

1. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → Troubleshooting
2. Check workflow logs in GitHub Actions
3. Run locally: [LOCAL_TESTING.md](LOCAL_TESTING.md)
4. Use [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

## FAQ

**Q: Is it safe?**
A: Yes. Credentials stored in GitHub Secrets (encrypted). Code runs in your GitHub account. Data goes to your Google Sheet.

**Q: What if I change banks?**
A: Add new bank sender to `src/config.py` → `BANK_SENDERS` list.

**Q: Can I test before going live?**
A: Yes! See [LOCAL_TESTING.md](LOCAL_TESTING.md) to run locally.

**Q: What if I miss a day?**
A: No problem. Run manually in GitHub Actions, or it catches up next day (25-hour lookback).

**Q: How much does it cost?**
A: ~₹10/month ($0.10) for Anthropic API. Everything else is free.

**Q: Can I use Outlook/Yahoo?**
A: Gmail only for now (IMAP support for others can be added).

**Q: Can I export data?**
A: Yes, Google Sheets can export to CSV/Excel anytime.

---

## Success Checklist

After setup, you should have:

- [x] ✅ in GitHub Actions for manual test run
- [x] Transactions visible in Google Sheet
- [x] Monthly tab created (e.g., "January 2026")
- [x] Categories look accurate
- [x] Amounts match your emails

**If all checked: You're successfully tracking expenses automatically! 🎉**

---

## Quick Links

| What | Where |
|------|-------|
| Generate Gmail App Password | https://myaccount.google.com/apppasswords |
| Get Anthropic API Key | https://console.anthropic.com/ |
| Google Cloud Console | https://console.cloud.google.com/ |
| Your Google Sheet | Open from https://sheets.google.com/ |
| GitHub Actions | https://github.com/YOUR_USER/gringotts/actions |

---

**Ready? Start with Step 1 above! ⬆️**
