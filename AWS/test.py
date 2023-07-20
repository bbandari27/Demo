import boto3

def role_exists(iam_client, role_name):
    try:
        response = iam_client.get_role(RoleName=role_name)
        return True
    except iam_client.exceptions.NoSuchEntityException:
        return False

def assume_role(role_arn):
    sts_client = boto3.client('sts')
    try:
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='AssumeRoleSession'
        )
        session = boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken']
        )
        print("Assumed 'AWSControlTowerExecution'.")
        return session
    except sts_client.exceptions.NoSuchEntityException:
        print("The 'AWSControlTowerExecution' does not exist or is not accessible.")
        return None

def disable_config_recorder(account_id, region):
    config_client = boto3.client('config', region_name=region)

    # Stop the Config Recorder
    try:
        print(f"Stopping the Config Recorder for Account ID: {account_id} in Region: {region}")
        #config_client.stop_configuration_recorder(ConfigurationRecorderName='default')
        print(f"Config Recorder stopped for Account ID: {account_id} in Region: {region}")
    except config_client.exceptions.NoSuchConfigurationRecorderException:
        print(f"No Config Recorder found in Account ID: {account_id} in Region: {region}")

    # Delete the Delivery Channel
    try:
        print(f"Deleting the Delivery Channel for Account ID: {account_id} in Region: {region}")
        #config_client.delete_delivery_channel()
        print(f"Delivery Channel deleted for Account ID: {account_id} in Region: {region}")
    except config_client.exceptions.NoSuchDeliveryChannelException:
        print(f"No Delivery Channel found in Account ID: {account_id} in Region: {region}")

    # Delete the Config Recorder
    try:
        print(f"Deleting the Config Recorder for Account ID: {account_id} in Region: {region}")
        #config_client.delete_configuration_recorder(ConfigurationRecorderName='default')
        print(f"Config Recorder deleted for Account ID: {account_id} in Region: {region}")
    except config_client.exceptions.NoSuchConfigurationRecorderException:
        print(f"No Config Recorder found in Account ID: {account_id} in Region: {region}")

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

def get_account_owner(org_client, account_id):
    try:
        response = org_client.describe_account(AccountId=account_id)
        account_owner = response['Account']['Arn']
        return account_owner
    except org_client.exceptions.AccountNotFoundException:
        return None

def move_account_to_managed_transition(org_client, account_id):
    try:
        # Move the account to 'managed-transition' OU (ou-gettheshit)
        #org_client.move_account(AccountId=account_id, SourceParentId='ou1', DestinationParentId='ou-gettheshit')
        print(f"Moved account {account_id} to 'managed-transition' OU.")
    except Exception as e:
        print(f"Failed to move account {account_id} to 'managed-transition' OU: {e}")

accounts_with_other_trails = []
control_tower_role_name = 'AWSControlTowerExecution'
ou_ids = ['ou1', 'ou2', 'ou3', 'ou4']
aws_regions = boto3.session.Session().get_available_regions('config')

for ou_id in ou_ids:
    print(f"Checking accounts in OU {ou_id}...")
    org_client = boto3.client('organizations')
    accounts = list_all_accounts_for_parent(org_client, ou_id)
    print(f"Number of accounts in OU {ou_id}: {len(accounts)}")

    for account in accounts:
        account_id = account['Id']

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
                    # Check if the account only has 'CustomTrailV2' CloudTrail
                    ct_client = iam_session.client('cloudtrail')
                    trails = ct_client.describe_trails()['trailList']
                    has_only_Custom_trail = len(trails) == 1 and trails[0]['Name'] == 'CustomTrailV2'

                    if has_only_Custom_trail:
                        # Disable AWS Config Recorder in all regions
                        for region in aws_regions:
                            disable_config_recorder(account_id, region)

                        # Move account to 'managed-transition' OU
                        move_account_to_managed_transition(org_client, account_id)

                    else:
                        # Step 2: Save account ID if there are other trails
                        accounts_with_other_trails.append(account_id)
                        print(f"Account {account['Name']}, {account_id}, {account_owner}  has other trails, skipping disabling and moving.")
            else:
                print(f"'AWSControlTowerExecution' does not exist in the account {account_id}.")

        except Exception as e:
            print(f"Error occurred in account {account_id}: {e}")

# Step 3: Save account IDs with other trails to a local text file
with open('accounts_with_other_trails.txt', 'w') as file:
    file.write("\n".join(accounts_with_other_trails))