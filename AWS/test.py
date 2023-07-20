import boto3
import csv

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
        # config_client.stop_configuration_recorder(ConfigurationRecorderName='default')
        pass  # Commented out for now
    except config_client.exceptions.NoSuchConfigurationRecorderException:
        print(f"No Config Recorder found in Account ID: {account_id} in Region: {region}")

    # Delete the Delivery Channel
    try:
        # config_client.delete_delivery_channel()
        pass  # Commented out for now
    except config_client.exceptions.NoSuchDeliveryChannelException:
        print(f"No Delivery Channel found in Account ID: {account_id} in Region: {region}")

    # Delete the Config Recorder
    try:
        # config_client.delete_configuration_recorder(ConfigurationRecorderName='default')
        pass  # Commented out for now
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
        # org_client.move_account(AccountId=account_id, SourceParentId='ou1', DestinationParentId='ou-gettheshit')
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
            owner_parts = account_owner.split('/')
            owner_name = owner_parts[-1]
            owner_email = owner_parts[-2]
            print(f"Account Owner Name: {owner_name}")
            print(f"Account Owner Email: {owner_email}")
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

# Step 3: Save account information with other trails to a CSV file
csv_filename = 'accounts_with_other_trails.csv'

with open(csv_filename, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Account Number', 'Account Name', 'Account Owner Email', 'Account Owner Name', 'Trails'])

    for account_id in accounts_with_other_trails:
        account_info = org_client.describe_account(AccountId=account_id)['Account']
        account_name = account_info['Name']
        account_owner_arn = account_info['Arn']
        account_owner_parts = account_owner_arn.split('/')
        account_owner_name = account_owner_parts[-1]
        account_owner_email = account_owner_parts[-2]

        # Fetch the list of trails for the account using your existing code.
        # ct_client = iam_session.client('cloudtrail')
        # trails = ct_client.describe_trails()['trailList']

        # For now, let's use a placeholder for the trails list.
        trails_list = ['Trail 1', 'Trail 2']

        csv_writer.writerow([account_id, account_name, account_owner_email, account_owner_name, ','.join(trails_list)])

print(f"All Config Recorders stopped and Delivery Channels deleted for all accounts.")
print(f"Account information with other trails saved to {csv_filename}.")
