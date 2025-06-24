import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import QuickBooksConfig, CategorizationRules

class QuickBooksClient:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.realm_id: Optional[str] = None
        self.base_url = "https://sandbox-quickbooks.api.intuit.com" if QuickBooksConfig.ENVIRONMENT == 'sandbox' else "https://quickbooks.api.intuit.com"
        
    def authenticate(self, auth_code: Optional[str] = None, realm_id: Optional[str] = None) -> bool:
        """Authenticate with QuickBooks API"""
        if auth_code and realm_id:
            # Exchange authorization code for access token
            token_url = f"{QuickBooksConfig.get_base_url()}/oauth2/v1/tokens/bearer"
            token_data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': QuickBooksConfig.REDIRECT_URI
            }
            
            # Ensure CLIENT_ID and CLIENT_SECRET are not None
            if not QuickBooksConfig.CLIENT_ID or not QuickBooksConfig.CLIENT_SECRET:
                raise Exception("CLIENT_ID and CLIENT_SECRET must be set in environment variables")
            
            response = requests.post(
                token_url,
                data=token_data,
                auth=(QuickBooksConfig.CLIENT_ID, QuickBooksConfig.CLIENT_SECRET)
            )
            
            if response.status_code == 200:
                token_info = response.json()
                self.access_token = token_info['access_token']
                self.refresh_token = token_info['refresh_token']
                self.realm_id = realm_id
                return True
            else:
                raise Exception(f"Authentication failed: {response.text}")
        else:
            # Generate authorization URL for user to visit
            auth_url = f"{QuickBooksConfig.get_base_url()}/connect/oauth2"
            params = {
                'client_id': QuickBooksConfig.CLIENT_ID or '',
                'response_type': 'code',
                'scope': 'com.intuit.quickbooks.accounting',
                'redirect_uri': QuickBooksConfig.REDIRECT_URI,
                'state': 'teststate'
            }
            
            auth_url_with_params = f"{auth_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            print(f"Please visit this URL to authorize the application: {auth_url_with_params}")
            return False
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            raise Exception("No refresh token available")
        
        token_url = f"{QuickBooksConfig.get_base_url()}/oauth2/v1/tokens/bearer"
        token_data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        # Ensure CLIENT_ID and CLIENT_SECRET are not None
        if not QuickBooksConfig.CLIENT_ID or not QuickBooksConfig.CLIENT_SECRET:
            raise Exception("CLIENT_ID and CLIENT_SECRET must be set in environment variables")
        
        response = requests.post(
            token_url,
            data=token_data,
            auth=(QuickBooksConfig.CLIENT_ID, QuickBooksConfig.CLIENT_SECRET)
        )
        
        if response.status_code == 200:
            token_info = response.json()
            self.access_token = token_info['access_token']
            if 'refresh_token' in token_info:
                self.refresh_token = token_info['refresh_token']
            return True
        else:
            raise Exception(f"Token refresh failed: {response.text}")
    
    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request to QuickBooks"""
        if not self.access_token or not self.realm_id:
            raise Exception("Not authenticated. Please authenticate first.")
        
        url = f"{self.base_url}/v3/company/{self.realm_id}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data or {})
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data or {})
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code == 401:
                # Token expired, try to refresh
                self.refresh_access_token()
                headers['Authorization'] = f'Bearer {self.access_token}'
                response = requests.request(method, url, headers=headers, json=data or {})
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def get_accounts(self) -> List[Dict]:
        """Get all accounts from QuickBooks"""
        response = self._make_api_request('GET', 'query?query=SELECT * FROM Account')
        return response.get('QueryResponse', {}).get('Account', [])
    
    def get_bank_accounts(self) -> List[Dict]:
        """Get only bank accounts from QuickBooks"""
        response = self._make_api_request('GET', 'query?query=SELECT * FROM Account WHERE AccountType = \'Bank\'')
        return response.get('QueryResponse', {}).get('Account', [])
    
    def get_transactions(self, account_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Get transactions for a specific account"""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        query = f"SELECT * FROM Transaction WHERE AccountRef = '{account_id}' AND TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        response = self._make_api_request('GET', f'query?query={query}')
        return response.get('QueryResponse', {}).get('Transaction', [])
    
    def get_uncategorized_transactions(self, account_id: str) -> List[Dict]:
        """Get uncategorized transactions for a specific account"""
        query = f"SELECT * FROM Transaction WHERE AccountRef = '{account_id}' AND Classification = 'Uncategorized'"
        response = self._make_api_request('GET', f'query?query={query}')
        return response.get('QueryResponse', {}).get('Transaction', [])
    
    def get_categories(self) -> List[Dict]:
        """Get all account categories from QuickBooks"""
        response = self._make_api_request('GET', 'query?query=SELECT * FROM Account WHERE AccountType IN (\'Income\', \'Expense\')')
        return response.get('QueryResponse', {}).get('Account', [])
    
    def update_transaction_category(self, transaction_id: str, category_id: str) -> Dict:
        """Update the category of a transaction"""
        # First get the current transaction
        response = self._make_api_request('GET', f'transaction/{transaction_id}')
        transaction = response.get('Transaction', {})
        
        # Update the category
        transaction['Line'][0]['AccountBasedExpenseLineDetail']['AccountRef']['value'] = category_id
        
        # Update the transaction
        update_data = {'sparse': True, 'Line': transaction['Line']}
        return self._make_api_request('POST', f'transaction', update_data)
    
    def categorize_transaction(self, transaction: Dict) -> Optional[str]:
        """Categorize a transaction based on rules"""
        if 'Line' not in transaction or not transaction['Line']:
            return None
        
        line = transaction['Line'][0]
        description = line.get('Description', '')
        amount = abs(float(line.get('Amount', 0)))
        
        # Get suggested category
        suggested_category = CategorizationRules.get_category_for_transaction(description, amount)
        
        return suggested_category
    
    def get_category_id_by_name(self, category_name: str) -> Optional[str]:
        """Get category ID by name"""
        categories = self.get_categories()
        for category in categories:
            if category.get('Name', '').lower() == category_name.lower():
                return category.get('Id')
        return None
    
    def create_category_if_not_exists(self, category_name: str, account_type: str = 'Expense') -> str:
        """Create a new category if it doesn't exist"""
        # Check if category already exists
        existing_id = self.get_category_id_by_name(category_name)
        if existing_id:
            return existing_id
        
        # Create new category
        category_data = {
            'Name': category_name,
            'AccountType': account_type,
            'AccountSubType': 'OtherExpense' if account_type == 'Expense' else 'OtherIncome'
        }
        
        response = self._make_api_request('POST', 'account', category_data)
        return response.get('Account', {}).get('Id')
    
    def categorize_all_transactions(self, account_id: str, auto_create_categories: bool = True) -> Dict:
        """Categorize all uncategorized transactions for an account"""
        transactions = self.get_uncategorized_transactions(account_id)
        results = {
            'total_transactions': len(transactions),
            'categorized': 0,
            'failed': 0,
            'errors': []
        }
        
        for transaction in transactions:
            try:
                suggested_category = self.categorize_transaction(transaction)
                if suggested_category:
                    # Get or create category
                    category_id = self.get_category_id_by_name(suggested_category)
                    if not category_id and auto_create_categories:
                        category_id = self.create_category_if_not_exists(suggested_category)
                    
                    if category_id:
                        # Update transaction
                        self.update_transaction_category(transaction['Id'], category_id)
                        results['categorized'] += 1
                        print(f"Categorized transaction '{transaction.get('DocNumber', 'N/A')}' as '{suggested_category}'")
                    else:
                        results['errors'].append(f"Could not find or create category: {suggested_category}")
                        results['failed'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                results['errors'].append(f"Error categorizing transaction {transaction.get('Id', 'N/A')}: {str(e)}")
                results['failed'] += 1
        
        return results
    
    def categorize_all_bank_accounts(self, auto_create_categories: bool = True) -> Dict:
        """Categorize transactions for all bank accounts"""
        bank_accounts = self.get_bank_accounts()
        overall_results = {
            'total_accounts': len(bank_accounts),
            'accounts_processed': 0,
            'total_transactions_categorized': 0,
            'total_errors': 0,
            'account_results': {}
        }
        
        for account in bank_accounts:
            account_name = account.get('Name', 'Unknown')
            print(f"\nProcessing account: {account_name}")
            
            try:
                results = self.categorize_all_transactions(account['Id'], auto_create_categories)
                overall_results['account_results'][account_name] = results
                overall_results['accounts_processed'] += 1
                overall_results['total_transactions_categorized'] += results['categorized']
                overall_results['total_errors'] += results['failed']
                
                print(f"Account {account_name}: {results['categorized']} transactions categorized, {results['failed']} failed")
                
            except Exception as e:
                error_msg = f"Error processing account {account_name}: {str(e)}"
                print(error_msg)
                overall_results['account_results'][account_name] = {'error': error_msg}
                overall_results['total_errors'] += 1
        
        return overall_results 