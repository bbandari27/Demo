import boto3

def disable_config_recorder(account_id, region):
    config_client = boto3.client('config', region_name=region)

    # Stop the Config Recorder
    try:
        config_client.stop_configuration_recorder(ConfigurationRecorderName='default')
        print(f"Config Recorder stopped for Account ID: {account_id} in Region: {region}")
    except config_client.exceptions.NoSuchConfigurationRecorderException:
        print(f"No Configuration Recorder found in Account ID: {account_id} in Region: {region}")

    # Delete the Delivery Channel
    try:
        config_client.delete_delivery_channel()
        print(f"Delivery Channel deleted for Account ID: {account_id} in Region: {region}")
    except config_client.exceptions.NoSuchDeliveryChannelException:
        print(f"No Delivery Channel found in Account ID: {account_id} in Region: {region}")

    # Delete the Configuration Recorder
    try:
        config_client.delete_configuration_recorder(ConfigurationRecorderName='default')
        print(f"Configuration Recorder deleted for Account ID: {account_id} in Region: {region}")
    except config_client.exceptions.NoSuchConfigurationRecorderException:
        print(f"No Configuration Recorder found in Account ID: {account_id} in Region: {region}")

def main():
    account_ids = ['ac1', 'ac2']  # Replace with your list of AWS account IDs

    for account_id in account_ids:
        print(f"Processing Account ID: {account_id}")
        regions = boto3.session.Session().get_available_regions('config')
        for region in regions:
            print(f"Processing Region: {region}")
            try:
                disable_config_recorder(account_id, region)
            except Exception as e:
                print(f"Error occurred in Region: {region}: {str(e)}")

if __name__ == "__main__":
    main()



import boto3

def disable_config_recorder(account_id, region):
    # The function remains the same as in the previous example

def main():
    account_ids = ['ac1', 'ac2', 'act3']  # Replace with your list of AWS account IDs

    for account_id in account_ids:
        if account_id == 'act3':
            print(f"Skipping processing Account ID: {account_id}")
            continue
        
        print(f"Processing Account ID: {account_id}")
        regions = boto3.session.Session().get_available_regions('config')
        for region in regions:
            print(f"Processing Region: {region}")
            try:
                disable_config_recorder(account_id, region)
            except Exception as e:
                print(f"Error occurred in Region: {region}: {str(e)}")

if __name__ == "__main__":
    main()


