import boto3

def assume_role(role_arn):
    sts_client = boto3.client('sts')
    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='AssumeRoleSession'
    )
    return boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken']
    )

def check_and_disable_cloudtrail(session, account_id, region):
    ct_client = session.client('cloudtrail', region_name=region)
    trails = ct_client.describe_trails()['trailList']

    for trail in trails:
        if trail['Name'] == 'elluciantrailv2':
            print(f"Found 'elluciantrailv2' CloudTrail in account {account_id}, region {region}.")
            if trail['IsLogging']:
                print("Disabling 'elluciantrailv2' CloudTrail...")
                ct_client.stop_logging(Name=trail['Name'])
                print(f"'elluciantrailv2' CloudTrail has been disabled.")
            else:
                print("'elluciantrailv2' CloudTrail is already disabled.")
            break
    else:
        print(f"'elluciantrailv2' CloudTrail not found in account {account_id}, region {region}.")

def main():
    control_tower_role_name = 'controltowerexecutionrole'
    ou_ids = ['ou-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', 'ou-yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy']

    for ou_id in ou_ids:
        print(f"Checking accounts in OU {ou_id}...")
        org_client = boto3.client('organizations')
        accounts = org_client.list_accounts_for_parent(ParentId=ou_id)['Accounts']

        for account in accounts:
            account_id = account['Id']
            print(f"\nChecking account: {account['Name']} (ID: {account_id})")
            try:
                iam_session = assume_role(f"arn:aws:iam::{account_id}:role/{control_tower_role_name}")
                print(f"Assumed role '{control_tower_role_name}' in account {account_id}.")

                # Get all available regions for the account
                ec2_client = iam_session.client('ec2')
                regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

                for region in regions:
                    print(f"Checking region: {region}")
                    check_and_disable_cloudtrail(iam_session, account_id, region)

            except Exception as e:
                print(f"Error occurred in account {account_id}: {e}")

if __name__ == "__main__":
    main()
