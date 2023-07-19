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

def check_and_disable_cloudtrail(session, trail):
    trail_region = trail['HomeRegion']
    ct_client = session.client('cloudtrail', region_name=trail_region)
    trail_name = trail['Name']

    print(f"Found '{trail_name}' CloudTrail in region {trail_region}.")
    trail_status = ct_client.get_trail_status(Name=trail_name)

    if trail_status['IsLogging']:
        print(f"'{trail_name}' CloudTrail is actively logging events.")
        print(f"Disabling '{trail_name}' CloudTrail in region {trail_region}...")
        #ct_client.stop_logging(Name=trail_name)
        print(f"'{trail_name}' CloudTrail has been disabled.")
    else:
        print(f"'{trail_name}' CloudTrail is already disabled.")

        print(f"Disabling '{trail_name}' CloudTrail in region {trail_region}...")

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

control_tower_role_name = 'AWSControlTowerExecution'
ou_ids = ['ou1', 'ou2', 'ou3', 'ou4']

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
        #process remaining accounts 
        print(f"\nChecking account: {account['Name']} (ID: {account_id})")
        try:
            iam_client = boto3.client('iam')
            if role_exists(iam_client, control_tower_role_name):
                iam_session = assume_role(f"arn:aws:iam::{account_id}:role/{control_tower_role_name}")
                if iam_session:
                    ct_client = iam_session.client('cloudtrail')
                    trails = ct_client.describe_trails()['trailList']

                    for trail in trails:
                        if 'Name' in trail and trail['Name'] == 'EllucianTrailV2':
                            check_and_disable_cloudtrail(iam_session, trail)
                        elif 'Name' in trail and len(trail['Name']) > 0:
                            print ("EllucianTrailV2 not found, but {trail} found".format(trail=trail['Name']))
                        else:
                            print ("No trail found")
            else:
                print(f"'AWSControlTowerExecution' does not exist in the account {account_id}.")

        except Exception as e:
            print(f"Error occurred in account {account_id}: {e}")
