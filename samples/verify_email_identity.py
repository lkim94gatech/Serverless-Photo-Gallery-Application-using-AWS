import boto3
from botocore.exceptions import ClientError
from env import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION

# Create a new SES resource and specify a region.
ses = boto3.client('ses',
                 region_name=AWS_REGION,
                 aws_access_key_id=AWS_ACCESS_KEY,
                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

email_address = "corporan@gatech.com"

try:
    # Verify email identity.
    response = ses.verify_email_identity(
        EmailAddress=email_address,
    )

    print(response)

# Display an error if something goes wrong.
except ClientError as e:
    print(e.response['Error']['Message'])