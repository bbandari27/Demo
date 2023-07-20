# ... (existing code)

def disable_config_recorder(account_id, region):
    # ... (existing code)

def list_all_accounts_for_parent(org_client, parent_id):
    # ... (existing code)

def get_account_owner(org_client, account_id):
    # ... (existing code)

def move_account_to_managed_transition(org_client, account_id):
    try:
        # Move the account to 'managed-transition' OU
        org_client.move_account(AccountId=account_id, SourceParentId='ou1', DestinationParentId='managed-transition')
        print(f"Moved account {account_id} to 'managed-transition' OU.")
    except Exception as e:
        print(f"Failed to move account {account_id} to 'managed-transition' OU: {e}")

control_tower_role_name = 'AWSControlTowerExecution'
ou_ids = ['ou-1', 'ou-2', 'ou-3', 'ou-4']
aws_regions = boto3.session.Session().get_available_regions('config')

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
                        print(f"Account {account_id} has other trails, skipping disabling and moving.")
            else:
                print(f"'AWSControlTowerExecution' does not exist in the account {account_id}.")

        except Exception as e:
            print(f"Error occurred in account {account_id}: {e}")
