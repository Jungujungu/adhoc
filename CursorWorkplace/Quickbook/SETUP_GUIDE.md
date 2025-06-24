# Quick Setup Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up QuickBooks API
1. Go to [https://developer.intuit.com/](https://developer.intuit.com/)
2. Create a new QuickBooks API app
3. Copy your Client ID and Client Secret

### 3. Configure Environment
```bash
# Copy the example file
cp env.example .env

# Edit .env with your credentials
QUICKBOOKS_CLIENT_ID=your_client_id_here
QUICKBOOKS_CLIENT_SECRET=your_client_secret_here
QUICKBOOKS_ENVIRONMENT=sandbox
```

### 4. Test Your Setup
```bash
python test_setup.py
```

### 5. Run the Automation
```bash
# First time (get authorization URL)
python main.py

# After authorization (replace with your values)
python main.py --auth-code YOUR_CODE --realm-id YOUR_REALM_ID
```

## 📁 Files Created

- `main.py` - Main automation script
- `quickbooks_client.py` - QuickBooks API client
- `config.py` - Configuration and categorization rules
- `test_setup.py` - Setup verification script
- `run.bat` - Windows launcher
- `run.sh` - Unix/Linux/Mac launcher
- `README.md` - Full documentation
- `requirements.txt` - Python dependencies
- `env.example` - Environment template

## 🎯 What It Does

1. **Logs into QuickBooks** using OAuth2
2. **Connects to your company** automatically
3. **Finds all bank accounts** in your QuickBooks
4. **Categorizes transactions** using intelligent rules
5. **Processes all accounts** automatically
6. **Creates missing categories** if needed
7. **Provides detailed reporting** of results

## 🔧 Customization

Edit `config.py` to modify categorization rules:

```python
# Add custom rules
CategorizationRules.add_custom_rule(
    category_name='my_expense',
    keywords=['my_keyword', 'another_keyword'],
    category='My Custom Category',
    account_type='Expense'
)
```

## 🛡️ Safety Features

- **Dry run mode**: Test without making changes
- **Error handling**: Graceful failure recovery
- **Detailed logging**: See exactly what's happening
- **Backup reporting**: Save results to JSON file

## 🆘 Need Help?

1. Run `python test_setup.py` to diagnose issues
2. Check the full `README.md` for detailed instructions
3. Use `--dry-run` flag to test safely
4. Review error messages in the output

## 🎉 Success!

Once running, you'll see:
- List of bank accounts found
- Transactions being categorized
- Summary of results
- Any errors or issues

The automation will save you hours of manual categorization work! 