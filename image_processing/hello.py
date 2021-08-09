import boto3

client = boto3.client("s3")


def handler(event, context):
    print("hello world!")
    return str(client.list_buckets())
