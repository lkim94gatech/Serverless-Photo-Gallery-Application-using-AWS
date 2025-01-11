# Serverless Photo Gallery Application using AWS

**Serverless Photo Gallery Application** is a cloud-based application using AWS services like **Lambda**, **API Gateway**, **S3**, **DynamoDB**, and **Cognito**. This application is built to explore the implementation of both **SQL** (Amazon RDS) and **NoSQL** (DynamoDB) environments. The system is deployed on an EC2 instance using Flask and showcases scalable and persistent solutions.
## Important Notice
**For security reasons, sensitive files such as keys, credentials, and configuration files will NOT be included in this repository.
---

## Features

### AWS Services Utilized
- **EC2**: Hosts the Flask application and manages resources.
- **S3**: Stores photos and thumbnails with public access.
- **RDS (MySQL)**: Relational database for SQL variant.
- **DynamoDB**: NoSQL database for the NoSQL variant.
- **IAM**: Ensures secure resource access through custom policies.
- **AWS SES**: Email confirmation for user registration.

### Application Highlights
- **Variants**:
  - **SQL**: Albums and photos stored in separate RDS tables.
  - **NoSQL**: Albums and photos stored in a single DynamoDB table.
- **User Management**:
  - User sign-up with email confirmation.
  - Secure login with hashed passwords.
  - Account cancellation.
- **Photo & Album Management**:
  - Add, delete, and update photos.
  - Create and delete albums.
- **Session Management**:
  - Temporary session tokens for secure navigation.
- **Data Transfer**:
  - File transfer between local machine and EC2 using `scp` or FileZilla.

---

## Getting Started

### Prerequisites
- **AWS Account**: For access to AWS services.
- **Python 3.9+**: To run the Flask application.
- **AWS CLI**: To manage AWS resources from the command line.

### Setup Instructions
1. **Launch EC2 Instance**:
   - Use **Ubuntu 20.04** with `t2.micro` instance type.
   - Attach a **Security Group** allowing necessary port access (e.g., 5000, 3306).
2. **Create AWS Resources**:
   - **RDS**: Configure MySQL database with a public endpoint.
   - **DynamoDB**: Create a `PhotoGallery` table with:
     - `albumID` (partition key)
     - `photoID` (sort key)
   - **S3 Bucket**: For storing photos and thumbnails.
3. **IAM User**:
   - Assign policies for `AmazonS3FullAccess` and `AmazonDynamoDBFullAccess`.
4. **Deploy Code**:
   - Update `env.py` with necessary environment variables.
   - Transfer the codebase to EC2 using `scp` or FileZilla.

---

## Running the Application

### Install Dependencies
Run the following commands on your EC2 instance:
```bash
sudo apt update
sudo apt install python3-pip
pip3 install exifread flask PyMySQL boto3 pytz bcrypt

```
## Running the Application

### Start Flask Application

#### SQL Variant:
```bash
python3 app.py
```

#### NoSQL Variant:
```bash
python3 app.py
```

## Testing

### User Management
- **Sign-Up**: Create an account with hashed password storage and email verification.
- **Log-In**: Authenticate using session tokens.
- **Cancel Account**: Delete user data and associated albums/photos.

### Photo Operations
- **Add Photo**: Upload and store photos in S3.
- **Delete Photo**: Remove selected photos.
- **Update Photo**: Modify titles, descriptions, and tags.

### Album Operations
- **Create Album**: Organize photos into albums.
- **Delete Album**: Remove albums along with associated photos.


