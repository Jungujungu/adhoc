#!/usr/bin/env python3
"""
QuickBooks Bank Transaction Categorization Automation

This script automates the process of:
1. Logging into QuickBooks
2. Selecting a designated client
3. Finding bank transactions
4. Categorizing all open items with specific rules
5. Repeating for all bank accounts

Usage:
    python main.py [--client-id CLIENT_ID] [--auto-create-categories] [--dry-run]
"""

import argparse
import sys
import json
from datetime import datetime
from typing import Optional
from quickbooks_client import QuickBooksClient
from config import QuickBooksConfig, CategorizationRules

def setup_environment():
    """Setup environment variables and configuration"""
    print("=== QuickBooks Bank Transaction Categorization ===")
    print(f"Environment: {QuickBooksConfig.ENVIRONMENT}")
    print(f"Base URL: {QuickBooksConfig.get_base_url()}")
    
    # Check if required environment variables are set
    if not QuickBooksConfig.CLIENT_ID or not QuickBooksConfig.CLIENT_SECRET:
        print("ERROR: QUICKBOOKS_CLIENT_ID and QUICKBOOKS_CLIENT_SECRET must be set in environment variables")
        print("Please create a .env file with the following content:")
        print("QUICKBOOKS_CLIENT_ID=your_client_id_here")
        print("QUICKBOOKS_CLIENT_SECRET=your_client_secret_here")
        print("QUICKBOOKS_ENVIRONMENT=sandbox  # or production")
        return False
    
    return True

def authenticate_quickbooks() -> Optional[QuickBooksClient]:
    """Authenticate with QuickBooks API"""
    print("\n=== Step 1: QuickBooks Authentication ===")
    
    client = QuickBooksClient()
    
    # Try to authenticate
    auth_success = client.authenticate()
    
    if not auth_success:
        print("\nTo complete authentication:")
        print("1. Visit the URL shown above")
        print("2. Log in to QuickBooks and authorize the application")
        print("3. Copy the authorization code from the redirect URL")
        print("4. Copy the realm ID (company ID) from the QuickBooks interface")
        print("5. Run this script again with the --auth-code and --realm-id parameters")
        return None
    
    print("✓ Authentication successful!")
    return client

def select_client(client: QuickBooksClient) -> Optional[str]:
    """Select a specific client/company to work with"""
    print("\n=== Step 2: Client Selection ===")
    
    try:
        # Get company info
        company_info = client._make_api_request('GET', 'companyinfo')
        company = company_info.get('CompanyInfo', {})
        
        company_name = company.get('CompanyName', 'Unknown Company')
        company_id = company.get('Id')
        
        print(f"Connected to company: {company_name}")
        print(f"Company ID: {company_id}")
        
        return company_id
        
    except Exception as e:
        print(f"Error getting company information: {str(e)}")
        return None

def get_bank_accounts(client: QuickBooksClient) -> list:
    """Get all bank accounts"""
    print("\n=== Step 3: Bank Account Discovery ===")
    
    try:
        bank_accounts = client.get_bank_accounts()
        
        if not bank_accounts:
            print("No bank accounts found in QuickBooks.")
            return []
        
        print(f"Found {len(bank_accounts)} bank account(s):")
        for i, account in enumerate(bank_accounts, 1):
            account_name = account.get('Name', 'Unknown')
            account_type = account.get('AccountType', 'Unknown')
            account_id = account.get('Id', 'Unknown')
            print(f"  {i}. {account_name} ({account_type}) - ID: {account_id}")
        
        return bank_accounts
        
    except Exception as e:
        print(f"Error getting bank accounts: {str(e)}")
        return []

def categorize_transactions_for_account(client: QuickBooksClient, account: dict, auto_create_categories: bool = True, dry_run: bool = False) -> dict:
    """Categorize transactions for a specific account"""
    account_name = account.get('Name', 'Unknown')
    account_id = account.get('Id')
    
    if not account_id:
        error_msg = f"No account ID found for account: {account_name}"
        print(f"✗ {error_msg}")
        return {
            'account_name': account_name,
            'error': error_msg,
            'total_transactions': 0,
            'categorized': 0,
            'failed': 0,
            'errors': [error_msg]
        }
    
    print(f"\n--- Processing Account: {account_name} ---")
    
    if dry_run:
        print("DRY RUN MODE: No changes will be made")
    
    try:
        # Get uncategorized transactions
        transactions = client.get_uncategorized_transactions(account_id)
        
        if not transactions:
            print(f"No uncategorized transactions found for {account_name}")
            return {
                'account_name': account_name,
                'total_transactions': 0,
                'categorized': 0,
                'failed': 0,
                'errors': []
            }
        
        print(f"Found {len(transactions)} uncategorized transactions")
        
        results = {
            'account_name': account_name,
            'total_transactions': len(transactions),
            'categorized': 0,
            'failed': 0,
            'errors': []
        }
        
        for transaction in transactions:
            try:
                # Get transaction details
                doc_number = transaction.get('DocNumber', 'N/A')
                description = transaction.get('Memo', 'No description')
                amount = transaction.get('TotalAmt', 0)
                
                print(f"  Processing: {doc_number} - {description} (${amount})")
                
                # Categorize transaction
                suggested_category = client.categorize_transaction(transaction)
                
                if suggested_category:
                    print(f"    Suggested category: {suggested_category}")
                    
                    if not dry_run:
                        # Get or create category
                        category_id = client.get_category_id_by_name(suggested_category)
                        if not category_id and auto_create_categories:
                            category_id = client.create_category_if_not_exists(suggested_category)
                        
                        if category_id:
                            # Update transaction
                            client.update_transaction_category(transaction['Id'], category_id)
                            results['categorized'] += 1
                            print(f"    ✓ Categorized as '{suggested_category}'")
                        else:
                            results['errors'].append(f"Could not find or create category: {suggested_category}")
                            results['failed'] += 1
                            print(f"    ✗ Failed to categorize: {suggested_category}")
                    else:
                        results['categorized'] += 1
                        print(f"    ✓ Would categorize as '{suggested_category}' (dry run)")
                else:
                    results['failed'] += 1
                    print(f"    ✗ No category suggested")
                    
            except Exception as e:
                error_msg = f"Error processing transaction {transaction.get('Id', 'N/A')}: {str(e)}"
                results['errors'].append(error_msg)
                results['failed'] += 1
                print(f"    ✗ Error: {str(e)}")
        
        return results
        
    except Exception as e:
        error_msg = f"Error processing account {account_name}: {str(e)}"
        print(f"✗ {error_msg}")
        return {
            'account_name': account_name,
            'error': error_msg,
            'total_transactions': 0,
            'categorized': 0,
            'failed': 0,
            'errors': [error_msg]
        }

def main():
    """Main function to orchestrate the automation"""
    parser = argparse.ArgumentParser(description='QuickBooks Bank Transaction Categorization Automation')
    parser.add_argument('--auth-code', help='QuickBooks authorization code')
    parser.add_argument('--realm-id', help='QuickBooks realm ID (company ID)')
    parser.add_argument('--auto-create-categories', action='store_true', 
                       help='Automatically create categories if they don\'t exist')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run in dry-run mode (no changes will be made)')
    parser.add_argument('--output-file', help='Output results to JSON file')
    
    args = parser.parse_args()
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Create QuickBooks client
    client = QuickBooksClient()
    
    # Authenticate
    if args.auth_code and args.realm_id:
        print("\n=== Step 1: QuickBooks Authentication ===")
        try:
            auth_success = client.authenticate(args.auth_code, args.realm_id)
            if auth_success:
                print("✓ Authentication successful!")
            else:
                print("✗ Authentication failed")
                sys.exit(1)
        except Exception as e:
            print(f"✗ Authentication error: {str(e)}")
            sys.exit(1)
    else:
        print("\n=== Step 1: QuickBooks Authentication ===")
        auth_success = client.authenticate()
        if not auth_success:
            print("\nTo complete authentication:")
            print("1. Visit the URL shown above")
            print("2. Log in to QuickBooks and authorize the application")
            print("3. Copy the authorization code from the redirect URL")
            print("4. Copy the realm ID (company ID) from the QuickBooks interface")
            print("5. Run this script again with the --auth-code and --realm-id parameters")
            sys.exit(1)
    
    # Select client
    company_id = select_client(client)
    if not company_id:
        print("✗ Failed to get company information")
        sys.exit(1)
    
    # Get bank accounts
    bank_accounts = get_bank_accounts(client)
    if not bank_accounts:
        print("✗ No bank accounts found")
        sys.exit(1)
    
    # Process each bank account
    print("\n=== Step 4: Transaction Categorization ===")
    
    overall_results = {
        'timestamp': datetime.now().isoformat(),
        'company_id': company_id,
        'total_accounts': len(bank_accounts),
        'accounts_processed': 0,
        'total_transactions_categorized': 0,
        'total_errors': 0,
        'account_results': {},
        'settings': {
            'auto_create_categories': args.auto_create_categories,
            'dry_run': args.dry_run
        }
    }
    
    for account in bank_accounts:
        results = categorize_transactions_for_account(
            client, 
            account, 
            auto_create_categories=args.auto_create_categories,
            dry_run=args.dry_run
        )
        
        overall_results['account_results'][account['Name']] = results
        overall_results['accounts_processed'] += 1
        
        if 'error' not in results:
            overall_results['total_transactions_categorized'] += results['categorized']
            overall_results['total_errors'] += results['failed']
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Total accounts processed: {overall_results['accounts_processed']}")
    print(f"Total transactions categorized: {overall_results['total_transactions_categorized']}")
    print(f"Total errors: {overall_results['total_errors']}")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE: No actual changes were made to QuickBooks")
    
    # Save results to file if requested
    if args.output_file:
        try:
            with open(args.output_file, 'w') as f:
                json.dump(overall_results, f, indent=2)
            print(f"\nResults saved to: {args.output_file}")
        except Exception as e:
            print(f"Error saving results to file: {str(e)}")
    
    print("\n=== Automation Complete ===")

if __name__ == "__main__":
    main() 