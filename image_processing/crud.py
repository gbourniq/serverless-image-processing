# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html

import json
import os
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

# def create(event, context):
#     response = table.put_item(
#         Item= {
#             'id': str(uuid.uuid1()),
#             'text': event['text'],
#             'checked': event['checked'] or False,
#             'info': {
#                 'plot': "plot",
#                 'rating': "rating"
#             },
#             'createdAt': datetime.utcnow().isoformat(),
#             'updatedAt': datetime.utcnow().isoformat(),
#         }
#     )
#     return response


def get(event, context):
    # print(event)
    try:
        item_id = event["pathParameters"]["id"]
        response = table.get_item(Key={"id": item_id})
        print(response)
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(
                response.get("Item", f"No item found with id {item_id}")
            ),
        }


def list(event, context):
    # scan_kwargs = {
    #     'FilterExpression': Key('year').between(*year_range),
    #     'ProjectionExpression': "#yr, title, info.rating",
    #     'ExpressionAttributeNames': {"#yr": "year"}
    # }
    scan_kwargs = {}

    done = False
    start_key = None
    results = []
    while not done:
        if start_key:
            scan_kwargs["ExclusiveStartKey"] = start_key
        response = table.scan(**scan_kwargs)
        results.append(response.get("Items", []))
        start_key = response.get("LastEvaluatedKey", None)
        done = start_key is None
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": str(results),
    }


def update(event, context):
    try:
        response = table.update_item(
            Key={"id": event["pathParameters"]["id"]},
            UpdateExpression="SET bucket_name = :bucket_name, updatedAt = :updatedAt",
            ExpressionAttributeValues={
                ":bucket_name": event["queryStringParameters"]["bucket_name"],
                ":updatedAt": datetime.utcnow().isoformat(),
            },
            ReturnValues="ALL_NEW",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            print(e.response["Error"]["Message"])
        else:
            raise
    else:
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {},
            "body": str(response),
        }


def delete(event, context):
    try:
        response = table.delete_item(
            Key={"id": event["pathParameters"]["id"]},
            # ConditionExpression="info.rating <= :val",
            # ExpressionAttributeValues={":val": Decimal(rating)}
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            print(e.response["Error"]["Message"])
        else:
            raise
    else:
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {},
            "body": str(response),
        }
