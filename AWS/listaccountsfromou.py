import boto3

def get_account_ids_in_ou(ou_id):
    # Create an AWS Organizations client
    org_client = boto3.client('organizations')

    # Get the list of accounts in the specified OU
    account_ids = []
    paginator = org_client.get_paginator('list_accounts_for_parent')
    response_iterator = paginator.paginate(
        ParentId=ou_id,
        PaginationConfig={'PageSize': 1000}  # Increase the page size if necessary
    )
    for page in response_iterator:
        for account in page['Accounts']:
            account_ids.append(account['Id'])

    return account_ids

# Specify the list of Organizational Unit (OU) IDs
ou_ids = ['ou-123456789012', 'ou-987654321098']  # Replace with your OU IDs

# Call the function to get the account IDs for each OU
for ou_id in ou_ids:
    print(f"Accounts in OU: {ou_id}")
    account_ids_list = get_account_ids_in_ou(ou_id)

    # Print the account IDs
    for account_id in account_ids_list:
        print(account_id)
    
    print("-------------------------")
