# ... (existing code)

# Step 1: Define a list to store account IDs with other trails
accounts_with_other_trails = []

for ou_id in ou_ids:
    print(f"Checking accounts in OU {ou_id}...")
    org_client = boto3.client('organizations')
    accounts = list_all_accounts_for_parent(org_client, ou_id)
    print (f"Number of accounts in OU {ou_id}: {len(accounts)}")

    for account in accounts:
        account_id = account['Id']

        #skip if the account is Raise Labs Inc
        if account_id == '030728503398':
            print(f"Skipping processing Raise Labs Inc Account, ID: {account_id}")
            continue

        # Get account owner information
        account_owner = get_account_owner(org_client, account_id)

        #process remaining accounts 
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
                    ct_client = iam_session.client('cloudtrail')
                    trails = ct_client.describe_trails()['trailList']

                    has_other_trails = False  # Flag to check if there are other trails in the account

                    for trail in trails:
                        if 'Name' in trail:
                            if trail['Name'] == 'EllucianTrailV2':
                                check_and_disable_cloudtrail(iam_session, trail)
                            else:
                                # If there are other trails, add the account ID to the list
                                has_other_trails = True

                    # Step 2 and Step 3: Save account ID if there are other trails and skip disabling
                    if has_other_trails:
                        accounts_with_other_trails.append(account_id)
            else:
                print(f"'AWSControlTowerExecution' does not exist in the account {account_id}.")

        except Exception as e:
            print(f"Error occurred in account {account_id}: {e}")

# Step 4: Save account IDs with other trails to a local text file
with open('accounts_with_other_trails.txt', 'w') as file:
    file.write("\n".join(accounts_with_other_trails))

