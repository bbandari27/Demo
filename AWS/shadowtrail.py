
import boto3

# ... (existing code remains the same)

def get_all_available_regions(service_name):
    # Get a list of all available AWS regions for a specific service
    session = boto3.Session()
    regions = session.get_available_regions(service_name)
    return regions

def trail_exists_in_region(cloudtrail_client, region):
    try:
        response = cloudtrail_client.describe_trails(trailNameList=['EllucianTrailV2'], includeShadowTrails=True, region=region)
        if 'trailList' in response and len(response['trailList']) > 0:
            return True
        else:
            return False
    except Exception as e:
        return False

def disable_cloudtrail_in_all_regions(account_id):
    assumed_role = assume_aws_controltower_role(account_id)

    if assumed_role:
        print(f"Assumed Role for Account {account_id}: {assumed_role['AssumedRoleUser']['Arn']}")
        # Create a new CloudTrail client using the temporary credentials
        cloudtrail_client = boto3.Session(profile_name='mb-admin').client('cloudtrail',
                                         aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                                         aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                                         aws_session_token=assumed_role['Credentials']['SessionToken']
                                         )

        # Get all available AWS regions
        regions = get_all_available_regions('cloudtrail')

        for region in regions:
            if trail_exists_in_region(cloudtrail_client, region):
                try:
                    cloudtrail_client.stop_logging(Name='EllucianTrailV2', Region=region)
                    print(f"CloudTrail 'EllucianTrailV2' disabled for Account {account_id} in region: {region}.")
                except Exception as e:
                    print(f"Error disabling CloudTrail 'EllucianTrailV2' in region: {region}. Error: {str(e)}")
            else:
                print(f"CloudTrail 'EllucianTrailV2' not found for Account {account_id} in region: {region}.")

# ... (existing code remains the same)

# Call the function to get the account IDs for each OU
account_ids_dict = get_account_ids_in_ous(ou_ids)

for ou_id, account_ids in account_ids_dict.items():
    print(f"OU ID: {ou_id}")
    print()
    for account_id in account_ids:
        print(f"Checking account: {account_id}")
        exists = check_execution_role(account_id)
        if exists:
            print("Controltowerexecutionrole exists.")
            # Disable 'EllucianTrailV2' in each account and in all regions
            disable_cloudtrail_in_all_regions(account_id)
        else:
            print("Controltowerexecutionrole does not exist.")
        print("-------------------------")
