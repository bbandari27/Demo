import boto3

def disable_cloudtrail(account_id):
    # Create an AWS STS client to assume the IAM role
    sts_client = boto3.client('sts')

    # Assume the IAM role in the individual account
    try:
        assumed_role = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/caeassumerole",
            RoleSessionName='AssumeRoleSession'
        )
        # Create a new CloudTrail client using the temporary credentials
        cloudtrail_client = boto3.client('cloudtrail',
                                         aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                                         aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                                         aws_session_token=assumed_role['Credentials']['SessionToken']
                                         )

        # Check if the 'trailv2' exists
        response = cloudtrail_client.describe_trails(trailNameList=['trailv2'])

        if 'trailList' in response and len(response['trailList']) > 0:
            # Disable the CloudTrail trail
            cloudtrail_client.stop_logging(Name='trailv2')
            return True

        return False

    except Exception as e:
        return False

# Specify the list of account IDs
account_ids_list = ['a1', 'a2', 'a3', 'a4']  # Replace with your account IDs

# Check and disable 'trailv2' in each account
for account_id in account_ids_list:
    print(f"Checking account: {account_id}")
    exists = disable_cloudtrail(account_id)
    if exists:
        print("CloudTrail 'trailv2' found and disabled.")
    else:
        print("CloudTrail 'trailv2' not found.")
    print("-------------------------")
