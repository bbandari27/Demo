# ... (existing code)

# Step 1: Define a list to store account IDs with other trails
accounts_with_other_trails = []

for ou_id in ou_ids:
    print(f"Checking accounts in OU {ou_id}...")
    org_client = boto3.client('organizations')
    accounts = list_all_accounts_for_parent(org_client, ou_id)
    print(f"Number of accounts in OU {ou_id}: {len(accounts)}")

    for account in accounts:
        account_id = account['Id']

        # Skip if the accounts is Raise Labs Inc
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
            iam_client = boto3.client('iam')
            if role_exists(iam_client, control_tower_role_name):
                iam_session = assume_role(f"arn:aws:iam::{account_id}:role/{control_tower_role_name}")
                if iam_session:
                    # Check if the account only has 'EllucianTrailV2' CloudTrail
                    ct_client = iam_session.client('cloudtrail')
                    trails = ct_client.describe_trails()['trailList']
                    has_only_ellucian_trail = len(trails) == 1 and trails[0]['Name'] == 'EllucianTrailV2'

                    if has_only_ellucian_trail:
                        # Disable AWS Config Recorder in all regions
                        for region in aws_regions:
                            disable_config_recorder(account_id, region)

                        # Move account to 'managed-transition' OU
                        move_account_to_managed_transition(org_client, account_id)

                    else:
                        # Step 2: Save account ID if there are other trails
                        accounts_with_other_trails.append(account_id)
                        print(f"Account {account_id} has other trails, skipping disabling and moving.")
            else:
                print(f"'AWSControlTowerExecution' does not exist in the account {account_id}.")

        except Exception as e:
            print(f"Error occurred in account {account_id}: {e}")

# Step 3: Save account IDs with other trails to a local text file
with open('accounts_with_other_trails.txt', 'w') as file:
    file.write("\n".join(accounts_with_other_trails))
