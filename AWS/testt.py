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
        print ("stop_configuration_recorder")
        response = boto3.client('sts').get_caller_identity().get('Arn')
        print(response)
        config_client.stop_configuration_recorder(ConfigurationRecorderName='default')
    except config_client.exceptions.NoSuchConfigurationRecorderException:
        print(f"No Config Recorder found in Account ID: {account_id} in Region: {region}")

    # Delete the Delivery Channel
    try:
        print ("delete_delivery_channel")
        config_client.delete_delivery_channel(DeliveryChannelName='default')
    except config_client.exceptions.NoSuchDeliveryChannelException:
        print(f"No Delivery Channel found in Account ID: {account_id} in Region: {region}")

    # Delete the Config Recorder
    try:
        print ("delete_configuration_recorder")
        config_client.delete_configuration_recorder(ConfigurationRecorderName='default')
    except config_client.exceptions.NoSuchConfigurationRecorderException:
        print(f"No Config Recorder found in Account ID: {account_id} in Region: {region}")

def move_account_to_managed_transition(org_client, account_id):
    try:
        # Move the account to 'managed-transition' OU (ou-tpfl-q4mp6zqv)
        org_client.move_account(AccountId=account_id, SourceParentId='ou-tpfl-yzh2jwec', DestinationParentId='ou-tpfl-q4mp6zqv')
        print(f"Moved account {account_id} to 'managed-transition' OU.")
    except Exception as e:
        print(f"Failed to move account {account_id} to 'managed-transition' OU: {e}")

control_tower_role_name = 'AWSControlTowerExecution'
aws_regions = boto3.session.Session().get_available_regions('config')

account_id = 743362854151

# Process remaining accounts
print(f"\nChecking account (ID: {account_id})")

try:
    iam_client = boto3.client('iam')
    response = boto3.client('sts').get_caller_identity().get('Arn')
    print(response)
    if role_exists(iam_client, control_tower_role_name):
        iam_session = assume_role(f"arn:aws:iam::{account_id}:role/{control_tower_role_name}")
        response = boto3.client('sts').get_caller_identity().get('Arn')
        print(response)
        if iam_session:
            # Disable AWS Config Recorder in all regions
            for region in aws_regions:
                disable_config_recorder(account_id, region)
            # Move account to 'managed-transition' OU
            move_account_to_managed_transition(org_client, account_id)
    else:
        print(f"'AWSControlTowerExecution' does not exist in the account {account_id}.")

except Exception as e:
    print(f"Error occurred in account {account_id}: {e}")
