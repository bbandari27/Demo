import boto3
import json
from botocore.exceptions import ClientError

def is_tls_enabled(bucket_name, s3_client):
    try:
        bucket_policy_str = s3_client.get_bucket_policy(Bucket=bucket_name)['Policy']
        bucket_policy = json.loads(bucket_policy_str)
        statements = bucket_policy['Statement']

        # Check if the bucket policy includes a statement requiring TLS
        for statement in statements:
            if (
                'Action' in statement and 's3:*' in statement['Action'] and
                'Condition' in statement and 'Bool' in statement['Condition'] and
                'aws:SecureTransport' in statement['Condition']['Bool'] and
                statement['Condition']['Bool']['aws:SecureTransport'] == 'false'
            ):
                return False

        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            return False
        else:
            raise e

def main():
    try:
        session = boto3.Session()
        s3_client = session.client('s3')

        # List buckets
        response = s3_client.list_buckets()

        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            tls_enabled = is_tls_enabled(bucket_name, s3_client)

            if tls_enabled:
                print(f"TLS is enabled on {bucket_name}.")
            else:
                print(f"TLS is NOT enabled on {bucket_name}.")

    except Exception as e:
        print(f"Error: {e}. Check your AWS credentials configuration.")

if __name__ == "__main__":
    main()
