import boto3
from botocore.exceptions import ClientError
from env import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION

# Create a new SES resource and specify a region.
ses = boto3.client('ses',
                 region_name=AWS_REGION,
                 aws_access_key_id=AWS_ACCESS_KEY,
                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

SENDER = "MyOtherVerifiedEmailAddress@gatech.edu"
RECEIVER = "myVerifiedEmailAddress@gatech.edu"

# Try to send the email.
response = None
try:
    #Provide the contents of the email.
    response = ses.send_email(
        Destination={
            'ToAddresses': [RECEIVER],
        },
        Message={
            'Body': {
                'Text': {
                   'Data': 'This is an email from AWS SES',
                },
            },
            'Subject': {
               'Data': 'Hi, I’m sending this email from AWS SES'
            },
        },
        Source=SENDER
    )

# Display an error if something goes wrong.
except ClientError as e:
    print(e.response['Error']['Message'])

else:
    print(f"Email sent! Message ID: {response['MessageId']}")
