# IAM User access configuration
AWS_ACCESS_KEY="censored"
AWS_SECRET_ACCESS_KEY="censored"
AWS_REGION="us-east-1"

# S3 Bucket for photo objects
PHOTOGALLERY_S3_BUCKET_NAME="photobucket-kim-2024-4150"

# MySQL Configuration
RDS_DB_HOSTNAME= 'photogallerydb.cx6qm0gukoob.us-east-1.rds.amazonaws.com'
RDS_DB_USERNAME='root'
RDS_DB_PASSWORD='censored'
RDS_DB_NAME='photogallerydb'

# DynamoDB Table
DYNAMODB_TABLE='photogallerydb' #whichever you have mention during the setup
DYNAMODB_TABLE_USER = 'PhotoGalleryUser'
###### INSERT NEW ENVIRONMENT VARIEABLES HERE ######

HASH_SERIALIZER = "censored"

CURRENT_URL = "http://ec2-18-212-187-108.compute-1.amazonaws.com:5000"

SES_EMAIL_SOURCE = "lkim94@gatech.edu"

####################################################
