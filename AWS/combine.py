import boto3

# Function to get account IDs in an organizational unit (OU)
def get_account_ids_in_ou(ou_id):
    # Create an AWS Organizations client
    client = boto3.client('organizations')
    account_ids = []

    # Get the accounts in the OU
    response = client.list_accounts_for_parent(ParentId=ou_id)
    accounts = response['Accounts']
    account_ids.extend(account['Id'] for account in accounts)

    return account_ids

# Function to get account IDs in multiple OUs
def get_account_ids_in_ous(ou_ids):
    account_ids_dict = {}
    for ou_id in ou_ids:
        # Get account IDs in each OU
        account_ids = get_account_ids_in_ou(ou_id)
        account_ids_dict[ou_id] = account_ids

    return account_ids_dict

# Function to assume the AWS Control Tower Execution role
def assume_aws_controltower_role(account_id):
    # Create an AWS STS client to assume the IAM role
    sts_client = boto3.client('sts')

    # Assume the IAM role in the individual account
    try:
        assumed_role = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/AWSControlTowerExecution",
            RoleSessionName='AssumeRoleSession'
        )
        return assumed_role

    except Exception as e:
        return None

# Function to check if the AWS Control Tower Execution role exists in an account
def check_execution_role(account_id):
    assumed_role = assume_aws_controltower_role(account_id)

    if assumed_role:
        # Print the assumed role ARN
        print(f"Assumed Role for Account {account_id}: {assumed_role['AssumedRoleUser']['Arn']}")
        # Create a new IAM client using the temporary credentials
        iam_client = boto3.client('iam',
                                  aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                                  aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                                  aws_session_token=assumed_role['Credentials']['SessionToken']
                                  )

        # Check if the 'AWSControlTowerExecution' role exists
        try:
            response = iam_client.get_role(RoleName='AWSControlTowerExecution')
            return True
        except iam_client.exceptions.NoSuchEntityException:
            return False

    return False

# Function to disable the CloudTrail 'EllucianTrailV2' for an account
def disable_cloudtrail(account_id):
    assumed_role = assume_aws_controltower_role(account_id)

    if assumed_role:
        # Print the assumed role ARN
        print(f"Assumed Role for Account {account_id}: {assumed_role['AssumedRoleUser']['Arn']}")
        # Create a new CloudTrail client using the temporary credentials
        cloudtrail_client = boto3.client('cloudtrail',
                                         aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                                         aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                                         aws_session_token=assumed_role['Credentials']['SessionToken']
                                         )

        # Check if the 'EllucianTrailV2' exists
        try:
            response = cloudtrail_client.describe_trails(trailNameList=['EllucianTrailV2'])
            # print(response)

            if 'trailList' in response and len(response['trailList']) > 0:
                trail_status = response['trailList'][0]['IsLogging']
                if trail_status:
                    cloudtrail_client.stop_logging(Name='EllucianTrailV2')
                    print(f"CloudTrail 'EllucianTrailV2' disabled for Account {account_id}.")
                else:
                    print(f"CloudTrail 'EllucianTrailV2' is already disabled for Account {account_id}.")
                return True
            else: 
                print(f"CloudTrail 'EllucianTrailV2' not found for Account {account_id}.")

        except Exception as e:
            return False

    return False

# Specify the list of transition Organizational Unit (OU) IDs
ou_ids = ['ou-tpfl-yzh2jwec', "ou-tpfl-9149izqy", "ou-tpfl-5881urnf", "ou-tpfl-rl5fan53"]  # transition OUs

# Call the function to get the account IDs for each OU
account_ids_dict = get_account_ids_in_ous(ou_ids)

for ou_id, account_ids in account_ids_dict.items():
    print (f"OU ID: {ou_id}")
    print ()
    for account_id in account_ids:
        print(f"Checking account: {account_id}")
        exists = check_execution_role(account_id)
        if exists:
            print("Controltowerexecutionrole exists.")
            # Disable 'EllucianTrailV2' in each account
            disable_cloudtrail(account_id)
        else:
            print("Controltowerexecutionrole does not exist.")
        print("-------------------------")
