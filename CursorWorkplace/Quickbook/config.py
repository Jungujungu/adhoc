import os
from dotenv import load_dotenv

load_dotenv()

class QuickBooksConfig:
    # QuickBooks API Configuration
    CLIENT_ID = os.getenv('QUICKBOOKS_CLIENT_ID')
    CLIENT_SECRET = os.getenv('QUICKBOOKS_CLIENT_SECRET')
    REDIRECT_URI = os.getenv('QUICKBOOKS_REDIRECT_URI', 'http://localhost:8080/callback')
    ENVIRONMENT = os.getenv('QUICKBOOKS_ENVIRONMENT', 'sandbox')  # or 'production'
    
    # API Base URLs
    SANDBOX_BASE_URL = 'https://sandbox-accounts.platform.intuit.com'
    PRODUCTION_BASE_URL = 'https://accounts.platform.intuit.com'
    
    @classmethod
    def get_base_url(cls):
        return cls.SANDBOX_BASE_URL if cls.ENVIRONMENT == 'sandbox' else cls.PRODUCTION_BASE_URL

class CategorizationRules:
    """Rules for categorizing bank transactions"""
    
    # Default categorization rules - customize these based on your needs
    RULES = {
        'income': {
            'keywords': ['payment', 'deposit', 'transfer in', 'credit', 'refund'],
            'category': 'Income',
            'account_type': 'Income'
        },
        'expenses': {
            'office_supplies': {
                'keywords': ['staples', 'office depot', 'amazon office', 'paper', 'ink', 'printer'],
                'category': 'Office Supplies',
                'account_type': 'Expense'
            },
            'utilities': {
                'keywords': ['electric', 'gas', 'water', 'internet', 'phone', 'cable'],
                'category': 'Utilities',
                'account_type': 'Expense'
            },
            'travel': {
                'keywords': ['uber', 'lyft', 'hotel', 'airline', 'gas station', 'parking'],
                'category': 'Travel',
                'account_type': 'Expense'
            },
            'meals': {
                'keywords': ['restaurant', 'cafe', 'coffee', 'food', 'dining', 'grubhub', 'doordash'],
                'category': 'Meals and Entertainment',
                'account_type': 'Expense'
            },
            'software': {
                'keywords': ['adobe', 'microsoft', 'google', 'zoom', 'slack', 'subscription'],
                'category': 'Software and Subscriptions',
                'account_type': 'Expense'
            },
            'marketing': {
                'keywords': ['facebook', 'google ads', 'marketing', 'advertising', 'seo'],
                'category': 'Marketing and Advertising',
                'account_type': 'Expense'
            }
        }
    }
    
    @classmethod
    def get_category_for_transaction(cls, description, amount):
        """Determine the appropriate category for a transaction based on description and amount"""
        description_lower = description.lower()
        
        # Check for income
        if any(keyword in description_lower for keyword in cls.RULES['income']['keywords']):
            return cls.RULES['income']['category']
        
        # Check expense categories
        for category_name, category_rules in cls.RULES['expenses'].items():
            if any(keyword in description_lower for keyword in category_rules['keywords']):
                return category_rules['category']
        
        # Default category for uncategorized transactions
        return 'Uncategorized'
    
    @classmethod
    def add_custom_rule(cls, category_name, keywords, category, account_type='Expense'):
        """Add a custom categorization rule"""
        if 'expenses' not in cls.RULES:
            cls.RULES['expenses'] = {}
        
        cls.RULES['expenses'][category_name] = {
            'keywords': keywords,
            'category': category,
            'account_type': account_type
        } 