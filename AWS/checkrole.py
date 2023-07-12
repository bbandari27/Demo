import boto3

def check_execution_role(account_id):
    # Create an AWS STS client to assume the IAM role
    sts_client = boto3.client('sts')

    # Assume the IAM role in the individual account
    try:
        assumed_role = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/assumerole",
            RoleSessionName='AssumeRoleSession'
        )
        # Create a new IAM client using the temporary credentials
        iam_client = boto3.client('iam',
                                  aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                                  aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                                  aws_session_token=assumed_role['Credentials']['SessionToken']
                                  )

        # Check if the 'Controltowerexecutionrole' exists
        response = iam_client.get_role(RoleName='Controltowerexecutionrole')
        return True

    except Exception as e:
        return False

# Specify the list of account IDs
account_ids_list = ['account-id-1', 'account-id-2', 'account-id-3']  # Replace with your account IDs

# Check if the 'Controltowerexecutionrole' exists in each account
for account_id in account_ids_list:
    print(f"Checking account: {account_id}")
    exists = check_execution_role(account_id)
    if exists:
        print("Controltowerexecutionrole exists.")
    else:
        print("Controltowerexecutionrole does not exist.")
    print("-------------------------")
