# Gringotts - Complete Setup Guide for GitHub Actions

This guide will walk you through setting up Gringotts to run automatically every night via GitHub Actions.

---

## Prerequisites Checklist

Before you begin, you'll need:
- [ ] GitHub account
- [ ] Gmail account (you're using: jrajrohit33@gmail.com)
- [ ] Anthropic API account
- [ ] Google Cloud Platform account

---

## Step 1: Push Code to GitHub

### 1.1 Create a GitHub Repository

1. Go to https://github.com/new
2. Repository name: `gringotts` (or any name you prefer)
3. Description: "Automated expense tracker with Claude AI"
4. Choose **Private** (recommended for personal finance data)
5. Click "Create repository"

### 1.2 Push Your Code

```bash
cd /Users/jalemrajrohit/Documents/VibeCoding/gringotts

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit - Gringotts expense tracker"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/gringotts.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 2: Get Gmail App Password

Gmail app passwords allow applications to access your Gmail without using your main password.

### Steps:

1. **Enable 2-Step Verification** (if not already enabled)
   - Go to https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow the setup process

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other (Custom name)"
   - Enter name: "Gringotts"
   - Click "Generate"
   - **Copy the 16-character password** (format: xxxx xxxx xxxx xxxx)
   - **Save this password** - you'll use it as `EMAIL_PASSWORD` secret

> **Note**: You already have an app password (`qnxt nlip gdlu uhtk`), you can use this or generate a new one.

---

## Step 3: Get Anthropic API Key

### Steps:

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Click on your profile → "API Keys"
4. Click "Create Key"
5. Name: "Gringotts"
6. **Copy the API key** (starts with `sk-ant-`)
7. **Save this key** - you'll use it as `ANTHROPIC_API_KEY` secret

### Cost Estimate:
- Model: Claude Haiku 4.5
- Cost: ~$0.25 per million input tokens
- Expected usage: 2-5 API calls per day (for new merchants)
- **Monthly cost: < $0.10** (due to caching)

---

## Step 4: Set Up Google Sheets API

### 4.1 Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Project name: "Gringotts"
4. Click "Create"

### 4.2 Enable Google Sheets API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and click "Enable"

### 4.3 Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Service account details:
   - Name: `gringotts-bot`
   - Service account ID: `gringotts-bot` (auto-filled)
   - Description: "Service account for Gringotts expense tracker"
4. Click "Create and Continue"
5. Grant role: "Editor" (or just skip this)
6. Click "Done"

### 4.4 Create Service Account Key

1. Click on the service account you just created (`gringotts-bot@...`)
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Key type: **JSON**
5. Click "Create"
6. A JSON file will download - **save this file securely**
7. The JSON file content will be used as `GOOGLE_SERVICE_ACCOUNT` secret

The JSON should look like:
```json
{
  "type": "service_account",
  "project_id": "gringotts-...",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "gringotts-bot@....iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

---

## Step 5: Create Google Sheet

### 5.1 Create the Sheet

1. Go to https://sheets.google.com/
2. Click "+ Blank" to create a new spreadsheet
3. Rename it to "Gringotts - Expense Tracker"

### 5.2 Share with Service Account

1. Click the "Share" button (top right)
2. Paste the service account email: `gringotts-bot@YOUR_PROJECT.iam.gserviceaccount.com`
   - You can find this email in the JSON file (`client_email` field)
3. Give it "Editor" access
4. Uncheck "Notify people"
5. Click "Share"

### 5.3 Get Spreadsheet ID

The Spreadsheet ID is in the URL:
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
                                          ^^^^^^^^^^^^^^^^^^^
```

Example:
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
```
Spreadsheet ID: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

**Save this ID** - you'll use it as `SPREADSHEET_ID` secret

---

## Step 6: Add GitHub Secrets

### 6.1 Navigate to Secrets

1. Go to your GitHub repository
2. Click "Settings" tab
3. Click "Secrets and variables" → "Actions"
4. Click "New repository secret"

### 6.2 Add Each Secret

Add the following 5 secrets one by one:

#### Secret 1: EMAIL_ADDRESS
- Name: `EMAIL_ADDRESS`
- Value: `jrajrohit33@gmail.com`

#### Secret 2: EMAIL_PASSWORD
- Name: `EMAIL_PASSWORD`
- Value: Your 16-character Gmail app password (e.g., `qnxt nlip gdlu uhtk`)
- **Important**: Remove spaces if you copy-pasted (should be: `qnxtnlipgdluuhtk`)

#### Secret 3: ANTHROPIC_API_KEY
- Name: `ANTHROPIC_API_KEY`
- Value: Your Anthropic API key (starts with `sk-ant-`)

#### Secret 4: GOOGLE_SERVICE_ACCOUNT
- Name: `GOOGLE_SERVICE_ACCOUNT`
- Value: **Entire contents** of the service account JSON file
- **Important**: Copy the **entire JSON** including the curly braces `{ ... }`

Example:
```json
{"type":"service_account","project_id":"gringotts-123456","private_key_id":"abc123...","private_key":"-----BEGIN PRIVATE KEY-----\nMIIE...","client_email":"gringotts-bot@gringotts-123456.iam.gserviceaccount.com",...}
```

#### Secret 5: SPREADSHEET_ID
- Name: `SPREADSHEET_ID`
- Value: Your Google Sheets spreadsheet ID (from the URL)

---

## Step 7: Verify GitHub Actions Workflow

The workflow file is already created at `.github/workflows/nightly.yml`. Let's verify it's correct:

### View the Workflow

1. Go to your repository on GitHub
2. Click on `.github/workflows/nightly.yml`
3. Verify the contents match this structure:

```yaml
name: Gringotts Nightly Expense Tracker

on:
  schedule:
    # Run at 2:30 AM IST (9:00 PM UTC previous day)
    - cron: '0 21 * * *'
  workflow_dispatch:  # Allow manual triggering

jobs:
  fetch-and-process:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Gringotts
        env:
          EMAIL_ADDRESS: ${{ secrets.EMAIL_ADDRESS }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GOOGLE_SERVICE_ACCOUNT: ${{ secrets.GOOGLE_SERVICE_ACCOUNT }}
          SPREADSHEET_ID: ${{ secrets.SPREADSHEET_ID }}
        run: |
          python -m src.main

      - name: Upload logs on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: gringotts-logs
          retention-days: 7
```

---

## Step 8: Test the Workflow

### 8.1 Manual Test Run

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Click "Gringotts Nightly Expense Tracker" (left sidebar)
4. Click "Run workflow" button (top right)
5. Keep the branch as "main"
6. Click "Run workflow"

### 8.2 Monitor the Run

1. The workflow will appear in the list (may take a few seconds)
2. Click on the workflow run
3. Click on "fetch-and-process" job
4. Watch the logs in real-time

### 8.3 Expected Output

You should see:
```
Run Gringotts
============================================================
Gringotts - Automated Expense Tracker
============================================================
Loading configuration...
Initializing components...
Fetching emails from the last 25 hours...
Found X emails
Parsing transactions...
Categorizing transactions...
Removing duplicates...
Writing to Google Sheets...
============================================================
Summary:
  Emails fetched: X
  Transactions parsed: Y
  After deduplication: Z
  Written to Google Sheets: Z
============================================================
Transaction breakdown by category:
  Food & Dining: X
  Shopping: Y
  ...
Total Debits: ₹X,XXX.XX
Total Credits: ₹X,XXX.XX
Net: ₹X,XXX.XX
============================================================
Gringotts run completed successfully!
```

### 8.4 Verify in Google Sheets

1. Open your Google Sheet
2. You should see a new tab (e.g., "January 2026")
3. Verify transactions are populated with:
   - Date
   - Amount
   - Credit/Debit
   - Mode
   - Category
   - Merchant

---

## Step 9: Automatic Schedule

Once the manual test succeeds, the workflow will automatically run:
- **Every day at 2:30 AM IST** (9:00 PM UTC previous day)
- Processes emails from the last 25 hours
- Writes new transactions to Google Sheets

---

## Troubleshooting

### Issue: "Missing required environment variable"

**Solution**: Verify all 5 secrets are added correctly in GitHub Settings → Secrets

### Issue: "IMAP connection failed"

**Possible causes**:
1. Incorrect Gmail app password
2. 2-Step verification not enabled
3. App password has spaces (remove them)

**Solution**:
- Double-check the `EMAIL_PASSWORD` secret
- Ensure it's the 16-character app password (no spaces)

### Issue: "Failed to authenticate with Google Sheets"

**Possible causes**:
1. Service account JSON is incorrect
2. Spreadsheet not shared with service account
3. Google Sheets API not enabled

**Solution**:
1. Verify `GOOGLE_SERVICE_ACCOUNT` contains the entire JSON
2. Check that you shared the sheet with the service account email
3. Verify Google Sheets API is enabled in GCP

### Issue: "No emails found"

**This is normal if**:
- You haven't had any transactions in the last 25 hours
- The workflow runs successfully but finds 0 emails

**Check**:
- Look at the logs - it should say "No emails found. Exiting." (exit code 0)

### Issue: Workflow doesn't run automatically

**Solution**:
1. Check the workflow file is in `.github/workflows/nightly.yml`
2. Verify the cron syntax is correct
3. Wait for the scheduled time (2:30 AM IST)
4. GitHub Actions may have up to 10-minute delay for scheduled runs

---

## Monitoring and Maintenance

### View Workflow History

1. Go to "Actions" tab in your repository
2. All workflow runs are listed with:
   - ✅ Success (green checkmark)
   - ❌ Failure (red X)
   - ⏱️ In progress (yellow dot)

### Check Logs

1. Click on any workflow run
2. Click on "fetch-and-process"
3. Expand each step to see detailed logs

### Download Failure Logs

If a workflow fails:
1. Go to the failed workflow run
2. Scroll to the bottom
3. Look for "Artifacts" section
4. Download "gringotts-logs" (if available)

---

## Cost Summary

### Anthropic API (Claude Haiku)
- **Cost**: ~$0.25 per million input tokens
- **Expected**: 2-5 API calls/day for new merchants
- **Monthly**: < $0.10

### Google Sheets API
- **Cost**: Free
- **Quota**: 60 requests/minute

### GitHub Actions
- **Public repos**: Free
- **Private repos**: 2,000 minutes/month free
- **Usage**: ~2-3 minutes/day
- **Monthly**: ~60-90 minutes (well within free tier)

### Total Monthly Cost
- **~$0.10** (just Anthropic API)

---

## Security Best Practices

✅ **DO**:
- Use GitHub Secrets for all credentials
- Keep repository private (for personal finance data)
- Use Gmail app password (not main password)
- Use service account for Google Sheets (not personal OAuth)
- Review transaction categories periodically

❌ **DON'T**:
- Never commit secrets to the repository
- Never share your service account JSON file
- Never disable 2-Step verification on Gmail
- Never push `.env` files with credentials

---

## Next Steps

Once setup is complete:

1. ✅ Test the workflow manually (Step 8)
2. ✅ Verify transactions appear in Google Sheets
3. ✅ Wait for the first automatic run (2:30 AM IST)
4. ✅ Check the workflow history the next morning
5. ✅ Review and adjust categories as needed
6. ✅ Add more merchants to `MERCHANT_RULES` in `src/config.py` if desired

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the workflow logs in GitHub Actions
3. Verify all secrets are correctly set
4. Test individual components locally first

---

## Summary Checklist

Before going live, ensure you have:

- [ ] Created GitHub repository
- [ ] Pushed code to GitHub
- [ ] Generated Gmail app password
- [ ] Created Anthropic API key
- [ ] Set up Google Cloud project
- [ ] Enabled Google Sheets API
- [ ] Created service account and downloaded JSON
- [ ] Created Google Sheet and shared with service account
- [ ] Added all 5 GitHub Secrets
- [ ] Tested workflow manually
- [ ] Verified transactions in Google Sheet

🎉 **You're all set!** Gringotts will now automatically track your expenses every night!
