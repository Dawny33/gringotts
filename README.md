# Gringotts - Automated Expense Tracker

Named after the wizard bank in Harry Potter - because it guards and tracks your gold with magical precision.

## Overview

Gringotts is a personal finance automation system that:
- Runs nightly via GitHub Actions
- Fetches transaction emails via IMAP
- Parses them to extract transaction details
- Categorizes them using Claude Haiku
- Writes them to a Google Sheet with monthly tabs

## Features

- **Automated Email Fetching**: Connects to your email via IMAP and fetches bank/UPI transaction notifications
- **Smart Parsing**: Uses regex patterns to extract transaction details from 15+ Indian banks and UPI apps
- **AI Categorization**: Categorizes transactions using Claude Haiku with rule-based shortcuts to minimize API calls
- **Deduplication**: Automatically removes duplicate transactions (same transaction from email + SMS)
- **Monthly Sheets**: Organizes transactions in monthly tabs in Google Sheets
- **Caching**: Caches LLM categorization results to reduce API calls and costs

## Supported Banks & Payment Apps

- HDFC Bank
- ICICI Bank & Credit Cards
- Axis Bank
- IndusInd Bank
- American Express
- PhonePe
- Paytm
- Google Pay (via bank backends)

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GITHUB ACTIONS                                   │
│                      (Runs daily at 2:30 AM IST)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │    IMAP      │───▶│  Transaction │───▶│     Claude Haiku         │  │
│  │   Fetcher    │    │    Parser    │    │   (Categorization)       │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
│         │                                           │                    │
│         ▼                                           ▼                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     Google Sheets API                             │  │
│  │            (Monthly sheets: "January 2026", etc.)                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Setup

### Prerequisites

1. **Gmail Account** with App Password enabled
   - Go to [Google Account Settings](https://myaccount.google.com/security)
   - Enable 2-Step Verification
   - Generate an App Password for "Mail"

2. **Google Service Account** for Sheets API
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Sheets API
   - Create a Service Account and download JSON credentials
   - Share your Google Sheet with the service account email

3. **Anthropic API Key**
   - Sign up at [Anthropic Console](https://console.anthropic.com/)
   - Create an API key

4. **Google Sheet**
   - Create a new Google Sheet
   - Copy the Spreadsheet ID from the URL (the long string between `/d/` and `/edit`)
   - Share it with your service account email (with Editor access)

### Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd gringotts
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables for local testing:
   ```bash
   export EMAIL_ADDRESS="your@gmail.com"
   export EMAIL_PASSWORD="your-16-char-app-password"
   export ANTHROPIC_API_KEY="sk-ant-..."
   export GOOGLE_SERVICE_ACCOUNT='{"type":"service_account",...}'
   export SPREADSHEET_ID="your-sheet-id"
   ```

4. Run locally:
   ```bash
   python -m src.main
   ```

### GitHub Actions Setup

1. Go to your GitHub repository Settings > Secrets and variables > Actions

2. Add the following secrets:
   - `EMAIL_ADDRESS`: Your Gmail address
   - `EMAIL_PASSWORD`: Your Gmail app password (16 characters)
   - `ANTHROPIC_API_KEY`: Your Claude API key
   - `GOOGLE_SERVICE_ACCOUNT`: Full JSON content of service account credentials
   - `SPREADSHEET_ID`: Your Google Sheet ID

3. The workflow will run automatically every day at 2:30 AM IST

4. You can also trigger it manually:
   - Go to Actions tab
   - Select "Gringotts Nightly Expense Tracker"
   - Click "Run workflow"

## Project Structure

```
gringotts/
├── src/
│   ├── __init__.py
│   ├── main.py               # Entry point - orchestrates the pipeline
│   ├── email_fetcher.py      # IMAP client to fetch bank/UPI emails
│   ├── parser.py             # Regex-based transaction extraction
│   ├── categorizer.py        # LLM categorization with caching
│   ├── sheets.py             # Google Sheets writer
│   ├── deduplicator.py       # Remove duplicate transactions
│   └── config.py             # Constants and configuration
├── tests/
│   ├── __init__.py
│   ├── test_parser.py        # Unit tests for parser
│   ├── test_categorizer.py   # Unit tests for categorizer
│   └── fixtures/
│       └── sample_emails.json # Sample bank emails for testing
├── .github/
│   └── workflows/
│       └── nightly.yml       # GitHub Actions workflow
├── requirements.txt
└── README.md
```

## Categories

Transactions are automatically categorized into:
- Salary
- Food & Dining
- Groceries
- Shopping
- Utilities
- Rent
- Transportation
- Entertainment
- Healthcare
- Investment
- Transfer
- EMI
- Insurance
- Other

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## How It Works

1. **Email Fetching**: Connects to Gmail via IMAP and fetches emails from the last 25 hours from known bank senders
2. **Parsing**: Extracts transaction details (amount, merchant, type, mode) using regex patterns
3. **Categorization**:
   - First tries rule-based matching (e.g., "Swiggy" → "Food & Dining")
   - Falls back to Claude Haiku for unknown merchants
   - Caches LLM results to minimize API calls
4. **Deduplication**: Removes duplicate transactions based on amount, type, and time
5. **Writing**: Appends transactions to the appropriate monthly sheet in Google Sheets

## Cost Estimation

- **Anthropic API**: Claude Haiku is very cheap (~$0.25 per million input tokens)
  - With caching, expect ~2-5 API calls per day for new merchants
  - Monthly cost: < $0.10
- **Google Sheets API**: Free (60 requests/minute quota)
- **GitHub Actions**: Free for public repos, 2000 minutes/month for private repos

## Customization

### Adding New Banks

Edit `src/config.py` and add the bank's email sender to `BANK_SENDERS` list.

### Adding Regex Patterns

Edit `src/config.py` and add new patterns to the `PATTERNS` dictionary.

### Adding Merchant Rules

Edit `src/config.py` and add merchant keywords to `MERCHANT_RULES` dictionary.

## Troubleshooting

### No emails found
- Check that your Gmail app password is correct
- Verify that you have transaction emails in your inbox
- Check the time window (default: last 25 hours)

### Parsing failures
- Check the logs to see which emails failed to parse
- Add new regex patterns in `config.py` for your bank's email format

### Google Sheets authentication error
- Verify service account JSON is correct
- Ensure the sheet is shared with the service account email
- Check that Google Sheets API is enabled in your GCP project

## Security

- Never commit secrets to the repository
- Use GitHub Secrets for all credentials
- App passwords (not main password) for Gmail
- Service accounts (not personal OAuth) for Sheets

## Future Enhancements

- SMS support via email forwarding
- Dashboard/visualization
- Budget alerts
- Multi-account support
- Manual transaction entry via Telegram bot
- Receipt image parsing

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a PR.
