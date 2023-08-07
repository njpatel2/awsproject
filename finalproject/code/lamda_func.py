import os
import json
import boto3

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from botocore.exceptions import ClientError


configFile = open('AppConfig.json')
configData = json.load(configFile)

s3 = boto3.client('s3', aws_access_key_id=configData['AWS_ACCESS_KEY_ID'], aws_secret_access_key=configData['AWS_SECRET_ACCESS_KEY'], region_name=configData['REGION_NAME'])
ses_client = boto3.client('ses', aws_access_key_id=configData['AWS_ACCESS_KEY_ID'], aws_secret_access_key=configData['AWS_SECRET_ACCESS_KEY'], region_name=configData['REGION_NAME'])

# Dictionary to keep track of the number of times the link has been accessed
access_count = {}

def send_email(sender, recipient, file_path, s3_bucket, s3_object_key):
    BODY = f"""\
    <html>
      <body>
        <h1>File Uploader</h1>
        <p>File Received!!!!</p>
        <p>Download the file from the link below:</p>
        <a href="{generate_s3_presigned_url(s3_bucket, s3_object_key)}">Download File</a>
      </body>
    </html>
    """

    msg = MIMEMultipart('mixed')
    msg['Subject'] = "AWS image"
    msg['From'] = sender
    msg['To'] = recipient
    msg_body = MIMEMultipart('alternative')
    htmlpart = MIMEText(BODY.encode("utf-8"), 'html', "utf-8")
    msg_body.attach(htmlpart)
    msg.attach(msg_body)
    
    try:
        response = ses_client.send_raw_email(Source=sender, Destinations=[recipient], RawMessage={'Data': msg.as_string()})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email is sent")

def generate_s3_presigned_url(bucket_name, object_key, expiration=3600):
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': object_key},
        ExpiresIn=expiration
    )
    return url

def delete_file_from_s3(s3_bucket, s3_object_key):
    s3.delete_object(Bucket=s3_bucket, Key=s3_object_key)

def lambda_handler(event, context):
    record = event['Records'][0]
    s3_bucket = record['s3']['bucket']['name']
    s3_object_key = record['s3']['object']['key']
    
    s3.download_file(configData['BUCKET_NAME'], "emails/emails.json", '/tmp/emails.json')
    s3object_path = f'/tmp/1.png'
    s3.download_file(configData['BUCKET_NAME'], "1.png", "/tmp/1.png")       
    file_path = s3object_path
    emailsfile = json.load(open('/tmp/emails.json'))
    recipients = emailsfile['recipients']
    
    # Initialize access count for each recipient to 0
    for recipient in recipients:
        access_count[recipient] = 0

    for recipient in recipients:
        send_email(emailsfile['sender'], recipient, file_path, s3_bucket, s3_object_key)
        access_count[recipient] += 1
        
        # Check if all recipients have accessed the link
        if access_count[recipient] == 1:
            # Delete the file from S3 once all recipients have accessed the link
            delete_file_from_s3(s3_bucket, s3_object_key)
            print(f"File {s3_object_key} deleted from S3.")

    return {
        'statusCode': 200,
        'body': json.dumps({"response": "Success!!!!"})
    }
