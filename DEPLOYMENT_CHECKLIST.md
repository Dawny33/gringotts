# Deployment Checklist

Use this checklist to ensure everything is set up correctly before going live.

---

## Pre-Deployment

### ✅ Code Repository

- [ ] All code is in `/Users/jalemrajrohit/Documents/VibeCoding/gringotts`
- [ ] Git is initialized (`git init`)
- [ ] All files are added (`git add .`)
- [ ] Initial commit created (`git commit -m "Initial commit"`)
- [ ] `.gitignore` is present and excludes `.env`, `*.log`, `.category_cache.json`

### ✅ GitHub Repository

- [ ] Created GitHub repository at https://github.com/YOUR_USERNAME/gringotts
- [ ] Repository is set to **Private** (recommended for personal finance)
- [ ] Remote added (`git remote add origin https://github.com/YOUR_USERNAME/gringotts.git`)
- [ ] Code pushed to GitHub (`git push -u origin main`)
- [ ] Verify files visible in GitHub web interface

---

## Credentials Setup

### ✅ Gmail App Password

- [ ] 2-Step Verification enabled at https://myaccount.google.com/security
- [ ] App password generated at https://myaccount.google.com/apppasswords
- [ ] 16-character password copied (format: `xxxx xxxx xxxx xxxx`)
- [ ] Spaces removed from password (should be 16 chars, no spaces)
- [ ] Password saved securely

**Test it:**
```bash
# Test IMAP connection locally
export EMAIL_ADDRESS="jrajrohit33@gmail.com"
export EMAIL_PASSWORD="your-app-password-no-spaces"
python3 -c "
import imaplib
conn = imaplib.IMAP4_SSL('imap.gmail.com', 993)
conn.login('$EMAIL_ADDRESS', '$EMAIL_PASSWORD')
print('✅ Gmail connection successful!')
conn.logout()
"
```

### ✅ Anthropic API Key

- [ ] Account created at https://console.anthropic.com/
- [ ] API key generated
- [ ] Key starts with `sk-ant-`
- [ ] Key copied and saved securely
- [ ] Billing set up (credit card added for pay-as-you-go)

**Test it:**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key"
python3 -c "
from anthropic import Anthropic
client = Anthropic(api_key='$ANTHROPIC_API_KEY')
response = client.messages.create(
    model='claude-haiku-4-5-20251001',
    max_tokens=10,
    messages=[{'role': 'user', 'content': 'Hi'}]
)
print('✅ Anthropic API key valid!')
print(f'Response: {response.content[0].text}')
"
```

### ✅ Google Cloud Setup

- [ ] Project created at https://console.cloud.google.com/
- [ ] Project name: "Gringotts" (or your choice)
- [ ] Google Sheets API enabled
- [ ] Service account created: `gringotts-bot`
- [ ] Service account key (JSON) downloaded
- [ ] JSON file saved securely
- [ ] Service account email noted: `gringotts-bot@PROJECT.iam.gserviceaccount.com`

**Verify JSON structure:**
```bash
cat service-account.json | python3 -m json.tool
# Should show valid JSON with: type, project_id, private_key, client_email, etc.
```

### ✅ Google Sheet Setup

- [ ] New spreadsheet created at https://sheets.google.com/
- [ ] Spreadsheet renamed to "Gringotts - Expense Tracker"
- [ ] Shared with service account email (Editor access)
- [ ] "Notify people" unchecked when sharing
- [ ] Spreadsheet ID copied from URL
- [ ] Format: Long alphanumeric string between `/d/` and `/edit`

**Example:**
```
URL: https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
ID:  1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

---

## GitHub Secrets

### ✅ Add All 5 Secrets

Go to: GitHub repo → Settings → Secrets and variables → Actions → New repository secret

#### Secret 1: EMAIL_ADDRESS
- [ ] Name: `EMAIL_ADDRESS` (exact spelling)
- [ ] Value: `jrajrohit33@gmail.com`
- [ ] Saved

#### Secret 2: EMAIL_PASSWORD
- [ ] Name: `EMAIL_PASSWORD` (exact spelling)
- [ ] Value: Your 16-char app password WITHOUT spaces
- [ ] Example: `qnxtnlipgdluuhtk` (not `qnxt nlip gdlu uhtk`)
- [ ] Saved

#### Secret 3: ANTHROPIC_API_KEY
- [ ] Name: `ANTHROPIC_API_KEY` (exact spelling)
- [ ] Value: Your API key (starts with `sk-ant-`)
- [ ] Saved

#### Secret 4: GOOGLE_SERVICE_ACCOUNT
- [ ] Name: `GOOGLE_SERVICE_ACCOUNT` (exact spelling)
- [ ] Value: **Entire JSON content** from service account file
- [ ] Must be valid JSON (starts with `{` and ends with `}`)
- [ ] No extra spaces or line breaks
- [ ] Saved

**Tip:** Copy JSON like this:
```bash
cat service-account.json | tr -d '\n' | pbcopy
# Then paste into GitHub Secret value field
```

#### Secret 5: SPREADSHEET_ID
- [ ] Name: `SPREADSHEET_ID` (exact spelling)
- [ ] Value: Just the ID (not the full URL)
- [ ] Example: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
- [ ] Saved

### ✅ Verify Secrets

- [ ] All 5 secrets show in GitHub Settings → Secrets and variables → Actions
- [ ] Names are EXACTLY as specified (case-sensitive)
- [ ] No typos in secret names

---

## Workflow Verification

### ✅ Workflow File

- [ ] File exists at `.github/workflows/nightly.yml`
- [ ] File visible in GitHub repository
- [ ] Cron schedule is correct: `'0 21 * * *'` (2:30 AM IST)
- [ ] All environment variables match secret names

**Verify in GitHub:**
```
Repository → .github/workflows/nightly.yml → View file
```

### ✅ Manual Test Run

1. [ ] Go to GitHub repo → Actions tab
2. [ ] Click "Gringotts Nightly Expense Tracker" in left sidebar
3. [ ] Click "Run workflow" button (top right)
4. [ ] Select branch: `main`
5. [ ] Click green "Run workflow" button
6. [ ] Wait for workflow to appear (refresh page)
7. [ ] Click on the workflow run
8. [ ] Click on "fetch-and-process" job
9. [ ] Watch logs in real-time

**Expected output:**
```
Run Gringotts
============================================================
Gringotts - Automated Expense Tracker
============================================================
Loading configuration...
✓ Successfully connected to IMAP server
✓ Found X emails
✓ Parsed X transactions
✓ Categorized X transactions
✓ Wrote X transactions to Google Sheets
============================================================
Gringotts run completed successfully!
```

### ✅ Verify Results

- [ ] Workflow completed with green checkmark ✅
- [ ] No error messages in logs
- [ ] Open Google Sheet
- [ ] New tab created (e.g., "January 2026")
- [ ] Transactions visible in sheet
- [ ] Data looks correct: Date, Amount, Type, Mode, Category, Merchant

---

## Troubleshooting (If Test Fails)

### ❌ "Missing required environment variable: X"

**Fix:**
- [ ] Check secret name is EXACT (case-sensitive)
- [ ] Verify secret exists in GitHub Settings → Secrets
- [ ] Verify `.github/workflows/nightly.yml` references correct secret name

### ❌ "IMAP connection failed" or "Authentication failed"

**Fix:**
- [ ] Verify 2-Step Verification is enabled on Gmail
- [ ] Verify app password is correct (16 chars, no spaces)
- [ ] Try generating new app password
- [ ] Update `EMAIL_PASSWORD` secret in GitHub

### ❌ "Failed to authenticate with Google Sheets"

**Fix:**
- [ ] Verify JSON is valid (paste in https://jsonlint.com/)
- [ ] Verify entire JSON is in `GOOGLE_SERVICE_ACCOUNT` secret
- [ ] Verify sheet is shared with service account email
- [ ] Verify Google Sheets API is enabled in GCP

### ❌ "No emails found"

**This is OK if:**
- [ ] You genuinely had no transactions in last 25 hours
- [ ] Check logs say "No emails found. Exiting." (exit code 0)

**Fix if unexpected:**
- [ ] Verify bank senders in `src/config.py` match your banks
- [ ] Increase lookback period temporarily (edit `src/main.py`, line with `fetch_emails(hours=25)`)

### ❌ Other Errors

- [ ] Read error message carefully
- [ ] Check workflow logs for stack trace
- [ ] Search error message in `SETUP_GUIDE.md` → Troubleshooting section
- [ ] Try running locally first (see `LOCAL_TESTING.md`)

---

## Post-Deployment

### ✅ Monitor First Week

- [ ] **Day 1**: Check workflow ran automatically (2:30 AM IST)
- [ ] **Day 2**: Verify new transactions appeared in sheet
- [ ] **Day 3**: Check categories are accurate
- [ ] **Day 4-7**: Monitor for any failures

**How to check:**
- GitHub repo → Actions tab → See workflow runs
- Green ✅ = Success
- Red ❌ = Failed (check logs)

### ✅ Review & Optimize

After first week:

- [ ] Review transaction categories
- [ ] Add frequently-used merchants to `MERCHANT_RULES` in `src/config.py`
- [ ] Verify all banks are covered
- [ ] Check Anthropic API usage at https://console.anthropic.com/
- [ ] Verify monthly cost is as expected (~$0.10)

### ✅ Set Up Notifications (Optional)

- [ ] Enable GitHub Actions email notifications
- [ ] Set up Telegram bot (see `CUSTOMIZATION.md`)
- [ ] Set up email summary (see `CUSTOMIZATION.md`)

---

## Security Checklist

### ✅ Final Security Review

- [ ] Repository is **Private** (not Public)
- [ ] `.env` file is in `.gitignore`
- [ ] No credentials in code or commits
- [ ] Service account JSON file not in repository
- [ ] All secrets are in GitHub Secrets (not hardcoded)
- [ ] 2-Step Verification enabled on Gmail
- [ ] Using app password (not main Gmail password)

**Verify no sensitive data:**
```bash
# Check git history for credentials
git log --all --full-history --source --oneline | grep -i "password\|secret\|key"
# Should return nothing

# Check current files
grep -r "sk-ant-" . --exclude-dir=.git
grep -r "private_key" . --exclude-dir=.git
# Should return nothing (or only references in docs)
```

---

## Maintenance

### ✅ Regular Tasks

**Weekly:**
- [ ] Check workflow runs in GitHub Actions
- [ ] Verify transactions in Google Sheet

**Monthly:**
- [ ] Review categories for accuracy
- [ ] Check Anthropic API costs
- [ ] Add new merchants to rules if needed

**As Needed:**
- [ ] Update patterns when changing banks
- [ ] Add new bank senders
- [ ] Customize categories

---

## Rollback Plan

If something goes wrong:

```bash
# 1. Stop the workflow
# Go to GitHub repo → Settings → Actions → Disable Actions

# 2. Review logs
# Go to Actions tab → Click failed run → Review logs

# 3. Fix locally
cd /Users/jalemrajrohit/Documents/VibeCoding/gringotts
# Make fixes...

# 4. Test locally
python3 -m src.main

# 5. Push fix
git add .
git commit -m "Fix: description of fix"
git push

# 6. Re-enable Actions
# Go to Settings → Actions → Enable Actions
```

---

## Success Criteria

### ✅ Deployment is Successful When:

- [x] Manual workflow run completes successfully ✅
- [x] Transactions appear in Google Sheet
- [x] Data is accurate (amounts, categories, merchants)
- [x] First automatic run (next day 2:30 AM) succeeds
- [x] No errors in logs
- [x] Cost is within expectations

---

## 🎉 You're Live!

Once all checkboxes are complete:

✅ **Gringotts is now tracking your expenses automatically!**

What happens next:
- Every day at 2:30 AM IST, workflow runs automatically
- Emails from last 25 hours are fetched and processed
- Transactions are categorized and written to Google Sheets
- Monthly tabs are created automatically
- Cost: ~$0.10/month

**Enjoy your automated expense tracking! 🚀**

---

## Quick Reference

| Task | Command/Link |
|------|--------------|
| View workflow runs | GitHub → Actions tab |
| Check Google Sheet | Open your spreadsheet |
| Add GitHub Secret | Settings → Secrets and variables → Actions |
| View API usage | https://console.anthropic.com/ |
| Generate app password | https://myaccount.google.com/apppasswords |
| Test locally | `python3 -m src.main` |
| Run tests | `pytest tests/` |

---

## Need Help?

If stuck, check these in order:

1. **[Quick Reference](QUICK_REFERENCE.md)** - Common commands and solutions
2. **[Setup Guide](SETUP_GUIDE.md)** - Detailed setup instructions
3. **[Local Testing](LOCAL_TESTING.md)** - Test components locally
4. Workflow logs in GitHub Actions
5. Error messages in the logs

Most issues are:
- Typos in secret names (case-sensitive!)
- Missing spaces in app password removal
- JSON not properly formatted for service account
- Sheet not shared with service account
