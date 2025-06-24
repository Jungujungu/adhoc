# QuickBooks Bank Transaction Categorization Automation

This Python application automates the process of categorizing bank transactions in QuickBooks using intelligent rules-based categorization. It can process multiple bank accounts and automatically categorize transactions based on keywords and patterns.

## Features

- 🔐 **Secure Authentication**: OAuth2 authentication with QuickBooks API
- 🏦 **Multi-Account Support**: Process all bank accounts in your QuickBooks company
- 🧠 **Intelligent Categorization**: Rule-based categorization with customizable keywords
- 🔄 **Auto-Category Creation**: Automatically create new categories if they don't exist
- 🛡️ **Dry Run Mode**: Test categorization without making changes
- 📊 **Detailed Reporting**: Comprehensive results and error reporting
- ⚙️ **Customizable Rules**: Easy-to-modify categorization rules

## Prerequisites

1. **QuickBooks Developer Account**: Sign up at [https://developer.intuit.com/](https://developer.intuit.com/)
2. **Python 3.7+**: Ensure Python is installed on your system
3. **QuickBooks Company**: Access to a QuickBooks company with bank accounts

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd Quickbook
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env with your QuickBooks API credentials
   nano .env
   ```

## QuickBooks API Setup

1. **Create a QuickBooks App**:
   - Go to [https://developer.intuit.com/](https://developer.intuit.com/)
   - Sign in and create a new app
   - Choose "QuickBooks API" as the app type
   - Set the redirect URI to `http://localhost:8080/callback`

2. **Get API Credentials**:
   - Copy your Client ID and Client Secret
   - Update your `.env` file with these values

3. **Configure App Settings**:
   - In your QuickBooks app settings, add the following scopes:
     - `com.intuit.quickbooks.accounting`
   - Set the redirect URI to match your `.env` file

## Usage

### Basic Usage

1. **First-time setup** (get authorization URL):
   ```bash
   python main.py
   ```

2. **Complete authentication** (after visiting the authorization URL):
   ```bash
   python main.py --auth-code YOUR_AUTH_CODE --realm-id YOUR_REALM_ID
   ```

### Advanced Usage

**Dry run mode** (test without making changes):
```bash
python main.py --auth-code YOUR_AUTH_CODE --realm-id YOUR_REALM_ID --dry-run
```

**Auto-create missing categories**:
```bash
python main.py --auth-code YOUR_AUTH_CODE --realm-id YOUR_REALM_ID --auto-create-categories
```

**Save results to file**:
```bash
python main.py --auth-code YOUR_AUTH_CODE --realm-id YOUR_REALM_ID --output-file results.json
```

**Full example**:
```bash
python main.py --auth-code YOUR_AUTH_CODE --realm-id YOUR_REALM_ID --auto-create-categories --dry-run --output-file results.json
```

## Customization

### Modifying Categorization Rules

Edit `config.py` to customize categorization rules:

```python
# Add custom rules
CategorizationRules.add_custom_rule(
    category_name='custom_expense',
    keywords=['your_keyword', 'another_keyword'],
    category='Custom Expense Category',
    account_type='Expense'
)

# Or modify existing rules in the RULES dictionary
```

### Default Categories

The application comes with pre-configured rules for:
- **Income**: payments, deposits, transfers, credits, refunds
- **Office Supplies**: staples, office depot, amazon office, paper, ink, printer
- **Utilities**: electric, gas, water, internet, phone, cable
- **Travel**: uber, lyft, hotel, airline, gas station, parking
- **Meals**: restaurant, cafe, coffee, food, dining, grubhub, doordash
- **Software**: adobe, microsoft, google, zoom, slack, subscription
- **Marketing**: facebook, google ads, marketing, advertising, seo

## File Structure

```
Quickbook/
├── main.py                 # Main automation script
├── quickbooks_client.py    # QuickBooks API client
├── config.py              # Configuration and categorization rules
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── README.md             # This file
└── .env                  # Your environment variables (create this)
```

## Authentication Flow

1. **Initial Run**: The script generates an authorization URL
2. **User Authorization**: Visit the URL and log in to QuickBooks
3. **Get Credentials**: Copy the authorization code and realm ID from the redirect
4. **Complete Setup**: Run the script again with the credentials

## Error Handling

The application includes comprehensive error handling:
- **Network errors**: Automatic retry with token refresh
- **API errors**: Detailed error messages and logging
- **Missing categories**: Option to auto-create or skip
- **Invalid transactions**: Graceful handling of malformed data

## Security Notes

- Never commit your `.env` file to version control
- Keep your Client Secret secure
- Use sandbox environment for testing
- Regularly rotate your API credentials

## Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Check your Client ID and Client Secret
   - Ensure redirect URI matches your app settings
   - Verify you're using the correct environment (sandbox/production)

2. **"No bank accounts found"**
   - Ensure your QuickBooks company has bank accounts
   - Check that your app has the correct permissions

3. **"API request failed"**
   - Verify your access token hasn't expired
   - Check your internet connection
   - Ensure your QuickBooks company is accessible

### Getting Help

- Check the QuickBooks API documentation
- Review the error messages in the output
- Use dry-run mode to test without making changes
- Check the generated results file for detailed information

## License

This project is provided as-is for educational and automation purposes. Please ensure compliance with QuickBooks API terms of service and your organization's policies.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this automation tool. 