import os
import uuid
from io import BytesIO

import boto3
from PIL import Image, ImageOps

s3 = boto3.client("s3")
sqs = boto3.client("sqs")
size = int(os.getenv("THUMBNAIL_SIZE", 128))  # TODO: use SSM?
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.getenv("DYNAMODB_TABLE"))


def handler(event, context):
    # parse event
    # {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'eu-west-2', 'eventTime': '2021-07-14T09:20:10.061Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'A1OV8DMNC14NQD'}, 'requestParameters': {'sourceIPAddress': '78.245.14.6'}, 'responseElements': {'x-amz-request-id': 'BV4QESVNV697QPTQ', 'x-amz-id-2': 'xA78UYmmrbKQiNZK2Q2rIWpITU3cGuv1WmMogOf+HIiq4NRH3EVr0DjXOOWVHWMJFW3jt9L2SM7IFuN8YHd1BSkqticDHLGoktipfg/e8xU='}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'c28538f9-fa7b-4917-9d8f-e6f3e0af4b4a', 'bucket': {'name': 'gbournique-image-processing', 'ownerIdentity': {'principalId': 'A1OV8DMNC14NQD'}, 'arn': 'arn:aws:s3:::gbournique-image-processing'}, 'object': {'key': 'ILTQq.png', 'size': 41236, 'eTag': '51a9badf0faeeae28a635e4e1dc34ce8', 'sequencer': '0060EEAC52C52C8557'}}}]}
    print(event)
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    # only create a thumbnail on non thumbnail pictures
    if not key.endswith("_thumbnail.png"):
        # get the image
        image = get_s3_image(bucket, key)
        # resize the image
        thumbnail = image_to_thumbnail(image)
        # get the new filename
        thumbnail_key = new_filename(key)
        # upload the file
        url = upload_to_s3(bucket, thumbnail_key, thumbnail)
        # Put metadata to DynamoDB
        # TODO: Create a class for this
        put_metadata_to_dyndb(
            event["Records"][0]["eventSource"],
            event["Records"][0]["eventTime"],
            event["Records"][0]["eventName"],
            event["Records"][0]["requestParameters"]["sourceIPAddress"],
            event["Records"][0]["s3"]["bucket"]["name"],
            event["Records"][0]["s3"]["object"]["key"],
        )

        # send data to SQS to be picked up by slack notifications function
        queue_url = sqs.get_queue_url(QueueName=os.environ["SQS_NAME"])["QueueUrl"]
        message = f"New file uploaded to S3 at {event['Records'][0]['s3']['bucket']['name']}/{event['Records'][0]['s3']['object']['key']} from {event['Records'][0]['requestParameters']['sourceIPAddress']}"
        response = sqs.send_message(
            QueueUrl=queue_url, MessageBody=message, DelaySeconds=0
        )
        print(f"response from SQS: {response}")

        return {"statusCode": 200, "body": f"Thumbnail URL {url}"}


def put_metadata_to_dyndb(
    event_source, event_time, event_name, source_ip, bucket_name, object_key
):
    response = table.put_item(
        Item={
            "id": str(uuid.uuid1()),
            "event_source": event_source,
            "createdAt": event_time,
            "updatedAt": event_time,
            "event_name": event_name,
            "source_ip": source_ip,
            "bucket_name": bucket_name,
            "object_key": object_key,
        }
    )
    # check if successful or raise error?


def get_s3_image(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    imagecontent = response["Body"].read()

    file = BytesIO(imagecontent)
    img = Image.open(file)
    return img


def image_to_thumbnail(image):
    return ImageOps.fit(image, (size, size), Image.ANTIALIAS)


def new_filename(key):
    key_split = key.rsplit(".", 1)
    return key_split[0] + "_thumbnail.png"


def upload_to_s3(bucket, key, image):
    # We're saving the image into a BytesIO object to avoid writing to disk
    out_thumbnail = BytesIO()
    # You MUST specify the file type because there is no file name to discern
    # it from
    image.save(out_thumbnail, "PNG")
    out_thumbnail.seek(0)

    response = s3.put_object(
        ACL="public-read",
        Body=out_thumbnail,
        Bucket=bucket,
        ContentType="image/png",
        Key=key,
    )
    print(response)

    url = "{}/{}/{}".format(s3.meta.endpoint_url, bucket, key)
    return url


# from aws_lambda_powertools.utilities.parser import parse
# from lib.models import GithubWebhookEvent
# gh_event: GithubWebhookEvent = parse(event=payload, model=GithubWebhookEvent)

# import json
# from lib.slackapi import SlackAPI
# from lib.secrets import get_secret_or_environment
# from lib.github import Github
# from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

# from aws_lambda_powertools import Logger

# logger = Logger(service="main")

# @logger.inject_lambda_context
# def handler(event, context):
#   github_secret = get_secret_or_environment('GITHUB_WEBHOOK_SECRET')
#   slack_api_token = get_secret_or_environment('SLACK_API_TOKEN')

#   github = Github(secret=github_secret)
#   slack = SlackAPI(api_token=slack_api_token)

#   slack_messages = github.handle(event)
#   for message in slack_messages:
#     slack.send_message('general', attachments=message)

#   return {
#     "statusCode": 200,
#     "body": f"ok: sent {len(slack_messages)} messages"
#   }
