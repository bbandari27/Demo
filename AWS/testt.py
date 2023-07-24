def disable_config_recorder(iam_session, account_id, region):
    config_client = iam_session.client('config', region_name=region)

    # Rest of the function remains the same

# ... Rest of the script ...

if role_exists(iam_client, control_tower_role_name):
    iam_session = assume_role(f"arn:aws:iam::{account_id}:role/{control_tower_role_name}")
    response = boto3.client('sts').get_caller_identity().get('Arn')
    print(response)
    if iam_session:
        # Disable AWS Config Recorder in all regions
        for region in aws_regions:
            disable_config_recorder(iam_session, account_id, region)
        # Move account to 'managed-transition' OU
        move_account_to_managed_transition(org_client, account_id)
else:
    print(f"'AWSControlTowerExecution' does not exist in the account {account_id}.")
