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
        config_client.stop_configuration_recorder(ConfigurationRecorderName='default')
        print(f"Config Recorder stopped for Account ID: {account_id} in Region: {region}")
    except config_client.exceptions.NoSuchConfigurationRecorderException:
        print(f"No Config Recorder found in Account ID: {account_id} in Region: {region}")

    # Delete the Delivery Channel
    try:
        print(f"Deleting the Delivery Channel for Account ID: {account_id} in Region: {region}")
        config_client.delete_delivery_channel()
        print(f"Delivery Channel deleted for Account ID: {account_id} in Region: {region}")
    except config_client.exceptions.NoSuchDeliveryChannelException:
        print(f"No Delivery Channel found in Account ID: {account_id} in Region: {region}")

    # Delete the Config Recorder
    try:
        print(f"Deleting the Config Recorder for Account ID: {account_id} in Region: {region}")
        config_client.delete_configuration_recorder(ConfigurationRecorderName='default')
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
        org_client.move_account(AccountId=account_id, SourceParentId='ou1', DestinationParentId='ou-gettheshit')
        print(f"Moved account {account_id} to 'managed-transition' OU.")
    except Exception as e:
        print(f"Failed to move account {account_id} to 'managed-transition' OU: {e}")

control_tower_role_name = 'AWSControlTowerExecution'
ou_ids = ['ou-1', 'ou-2', 'ou-3', 'ou-4']

for ou_id in ou_ids:
    print(f"Checking accounts in OU {ou_id}...")
    org_client = boto3.client('organizations')
    accounts = list_all_accounts_for_parent(org_client, ou_id)
    print (f"Number of accounts in OU {ou_id}: {len(accounts)}")

    for account in accounts:
        account_id = account['Id']

        #skip if the accounts is Raise Labs Inc
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
                    # Disable AWS Config Recorder
                    disable_aws_config_recorder(iam_session)

                    # Move account to 'managed-transition' OU
                    move_account_to_managed_transition(org_client, account_id)
            else:
                print(f"'AWSControlTowerExecution' does not exist in the account {account_id}.")

        except Exception as e:
            print(f"Error occurred in account {account_id}: {e}")

