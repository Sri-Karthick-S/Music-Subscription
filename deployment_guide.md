Deployment Guide: Music Subscription App

This guide walks through how to run the Music Subscription Flask application both locally and on AWS EC2. It includes AWS setup, DynamoDB, Lambda integration, and deployment instructions.

🔧 Local Development Setup

1. Prerequisites

Python 3.x

Git Bash or any terminal

pip, virtualenv

AWS CLI configured locally

2. Clone the repository

git clone https://github.com/Sri-Karthick-S/Music-Subscription.git
cd Music-Subscription


3. Create and activate virtual environment

python -m venv venv
source venv/Scripts/activate  # On Windows Git Bash

4. Install dependencies

pip install -r requirements.txt

5. Set up AWS credentials

Ensure your AWS credentials are configured at C:\Users\<username>\.aws\credentials:

[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
aws_session_token = YOUR_SESSION_TOKEN  # if using temporary credentials

6. Run Flask app locally

python app.py

Access the app at: http://127.0.0.1:505

EC2 Deployment

1. Launch EC2 Instance

OS: Ubuntu 24.04

Instance type: t2.micro (free tier)

Key pair: Use existing or create a .pem file

Allow port 22 (SSH) and port 5050 (custom TCP) in Security Group

2. Connect to EC2

ssh -i "labsuser.pem" ubuntu@<EC2_PUBLIC_IP>

3. Install Dependencies on EC2

sudo apt update && sudo apt install python3-venv python3-pip unzip -y

4. Clone and Setup App

git clone https://github.com/Sri-Karthick-S/Music-Subscription.git
cd Music-Subscription
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

5. Configure AWS credentials in EC2

aws configure

Paste the access key, secret, and region (us-east-1) and save.
Ensure ~/.aws/credentials includes:

[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
aws_session_token = YOUR_SESSION_TOKEN  # if needed

6. Run Flask App on EC2

python3 app.py

7. Access the app

In your browser: http://<EC2_PUBLIC_IP>:5050

Make sure port 5050 is open in the EC2 security group settings.
