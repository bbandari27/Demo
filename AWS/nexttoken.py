import boto3

# ... (existing code)

def list_all_accounts_for_parent(org_client, parent_id):
    all_accounts = []
    next_token = None

    while True:
        if next_token:
            response = org_client.list_accounts_for_parent(ParentId=parent_id, NextToken=next_token)
        else:
            response = org_client.list_accounts_for_parent(ParentId=parent_id)

        all_accounts.extend(response['Accounts'])
        next_token = response.get('NextToken')
        if not next_token:
            break

    return all_accounts

ou_ids = ['ou1', 'ou2', 'ou3', 'ou4']

for ou_id in ou_ids:
    print(f"Checking accounts in OU {ou_id}...")
    org_client = boto3.client('organizations')
    accounts = list_all_accounts_for_parent(org_client, ou_id)

    # Print the number of accounts in the organization
    print(f"Number of accounts in OU {ou_id}: {len(accounts)}")

    for account in accounts:
        account_id = account['Id']
        #skip if the accounts is Raise Labs Inc
        if account_id == 'accountdead':
            print(f"Skipping processing Raise Labs Inc Account, ID: {account_id}")
            continue
        #process remaining accounts 
        print(f"\nChecking account: {account['Name']} (ID: {account_id})")
        try:
            # ... (existing code)
        except Exception as e:
            print(f"Error occurred in account {account_id}: {e}")
