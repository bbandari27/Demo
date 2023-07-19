import boto3

def role_exists(iam_client, role_name):
    try:
        # Check if the IAM role exists
        response = iam_client.get_role(RoleName=role_name)
        return True
    except iam_client.exceptions.NoSuchEntityException:
        return False

def assume_role(role_arn):
    sts_client = boto3.client('sts')
    try:
        # Assume the provided IAM role
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='AssumeRoleSession'
        )
        session = boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken']
        )
        print(f"Assumed role: {role_arn}")
        return session
    except sts_client.exceptions.NoSuchEntityException:
        print("The specified role does not exist or is not accessible.")
        return None

def disable_aws_config_recorder(session):
    config_client = session.client('config')
    recorder_status = config_client.describe_configuration_recorder_status()
    if recorder_status['ConfigurationRecordersStatus'][0]['recording']:
        print("AWS Config Recorder is actively recording.")
        print("Disabling AWS Config Recorder...")
        config_client.stop_configuration_recorder(ConfigurationRecorderName='default')
        print("AWS Config Recorder has been disabled.")
    else:
        print("AWS Config Recorder is already disabled.")

def move_account_to_managed_transition(org_client, account_id):
    try:
        # Move the account to 'managed-transition' OU (ou-gettheshit)
        org_client.move_account(AccountId=account_id, SourceParentId='ou1', DestinationParentId='ou-gettheshit')
        print(f"Moved account {account_id} to 'managed-transition' OU.")
    except Exception as e:
        print(f"Failed to move account {account_id} to 'managed-transition' OU: {e}")

def list_all_accounts_for_parent(org_client, parent_id):
    # ... (existing code for pagination)

# ... (existing code for 'ou_ids' loop)

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
