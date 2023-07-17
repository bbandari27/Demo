import boto3

def get_account_ids_in_ou(ou_id):
    # Create an AWS Organizations client
    client = boto3.client('organizations')
    account_ids = []

    response = client.list_accounts_for_parent(ParentId=ou_id)
    accounts = response['Accounts']
    account_ids.extend(account['Id'] for account in accounts)

    return account_ids

def get_account_ids_in_ous(ou_ids):
    account_ids_dict = {}
    for ou_id in ou_ids:
        account_ids = get_account_ids_in_ou(ou_id)
        account_ids_dict[ou_id] = account_ids

    return account_ids_dict

def check_execution_role(account_id):
    # Create an AWS STS client to assume the IAM role
    sts_client = boto3.client('sts')

    # Assume the IAM role in the individual account
    try:
        assumed_role = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/AWSControlTowerExecution",
            RoleSessionName='AssumeRoleSession'
        )
        # Create a new IAM client using the temporary credentials
        iam_client = boto3.client('iam',
                                  aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                                  aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                                  aws_session_token=assumed_role['Credentials']['SessionToken']
                                  )

        # Check if the 'Controltowerexecutionrole' exists
        response = iam_client.get_role(RoleName='AWSControlTowerExecution')
        return True

    except Exception as e:
        return False

def disable_cloudtrail(account_id):
    # Create an AWS STS client to assume the IAM role
    sts_client = boto3.client('sts')

    # Assume the IAM role in the individual account
    try:
        assumed_role = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/AWSControlTowerExecution",
            RoleSessionName='AssumeRoleSession'
        )
        # Create a new CloudTrail client using the temporary credentials
        cloudtrail_client = boto3.client('cloudtrail',
                                         aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                                         aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                                         aws_session_token=assumed_role['Credentials']['SessionToken']
                                         )

        # Check if the 'EllucianTrailV2' exists
        response = cloudtrail_client.describe_trails(trailNameList=['EllucianTrailV2'])
        # print(response)

        if 'trailList' in response and len(response['trailList']) > 0:
            # Disable the CloudTrail trail
            #cloudtrail_client.stop_logging(Name='EllucianTrailV2')
            print ("CloudTrail 'EllucianTrailV2' found and not disabled.")
            return True
        else: 
            print("CloudTrail 'EllucianTrailV2' not found.")

        return False

    except Exception as e:
        return False

# Specify the list of transition Organizational Unit (OU) IDs
ou_ids = ['ou-tpfl-yzh2jwec', "ou-tpfl-9149izqy", "ou-tpfl-5881urnf", "ou-tpfl-rl5fan53"]  # transition OUs

# Call the function to get the account IDs for each OU
account_ids_dict = get_account_ids_in_ous(ou_ids)

for ou_id, account_ids in account_ids_dict.items():
    print (f"OU ID: {ou_id}")
    # print (f"Account IDs: {account_ids}")
    print ()
    for account_id in account_ids:
        print(f"Checking account: {account_id}")
        exists = check_execution_role(account_id)
        if exists:
            print("Controltowerexecutionrole exists.")
            #disable 'EllucianTrailV2' in each account
            disable_cloudtrail(account_id)
        else:
            print("Controltowerexecutionrole does not exist.")
        print("-------------------------")
