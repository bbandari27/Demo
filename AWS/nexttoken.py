import boto3

# ... (existing code)

def get_account_owner(org_client, account_id):
    try:
        response = org_client.describe_account(AccountId=account_id)
        account_owner = response['Account']['Arn']
        return account_owner
    except org_client.exceptions.AccountNotFoundException:
        return None

# ... (existing code)

control_tower_role_name = 'AWSControlTowerExecution'
ou_ids = ['ou1', 'ou2', 'ou3', 'ou4']

for ou_id in ou_ids:
    print(f"Checking accounts in OU {ou_id}...")
    org_client = boto3.client('organizations')
    accounts = list_all_accounts_for_parent(org_client, ou_id)

    print(f"Number of accounts in OU {ou_id}: {len(accounts)}")
    for account in accounts:
        account_id = account['Id']
        # skip if the account is Raise Labs Inc
        if account_id == '030728503398':
            print(f"Skipping processing Raise Labs Inc Account, ID: {account_id}")
            continue
        
        # Get account owner information
        account_owner = get_account_owner(org_client, account_id)
        
        # Process remaining accounts 
        print(f"\nChecking account: {account['Name']} (ID: {account_id})")
        if account_owner:
            print(f"Account Owner: {account_owner}")
        else:
            print("Account owner information not available.")
        try:
            # ... (existing code)
        except Exception as e:
            print(f"Error occurred in account {account_id}: {e}")
