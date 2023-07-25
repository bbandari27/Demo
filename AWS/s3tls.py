import boto3
from botocore.exceptions import ProfileNotFound

def is_tls_enabled(bucket_name, s3_client):
    try:
        bucket_policy = s3_client.get_bucket_policy(Bucket=bucket_name)

        # Check if the bucket policy includes a statement requiring TLS
        for statement in bucket_policy['Policy']['Statement']:
            if (
                'Action' in statement and 's3:*' in statement['Action'] and
                'Condition' in statement and 'Bool' in statement['Condition'] and
                'aws:SecureTransport' in statement['Condition']['Bool'] and
                statement['Condition']['Bool']['aws:SecureTransport'] == 'false'
            ):
                return False

        return True
    except s3_client.exceptions.NoSuchBucketPolicy:
        return False

def main():
    try:
        session = boto3.Session(profile_name='YOUR_SSO_PROFILE_NAME')
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

    except ProfileNotFound as e:
        print(f"Error: {e}. Check if the SSO profile is configured correctly.")

if __name__ == "__main__":
    main()
