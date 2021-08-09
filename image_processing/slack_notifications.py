from helpers.slackapi import SlackAPI


def handler(event, context):
    """Lambda function to forward SQS messages to Slack"""

    sqs_messages = []
    for record in event["Records"]:
        payload = record["body"]
        print(f"SQS payload: {payload}")
        sqs_messages.append(payload)

    # slack_api_token = get_secret_or_environment('SLACK_API_TOKEN')
    slack = SlackAPI(
        api_token="xoxb-1049093030724-2152114188067-ARH8HzGIuoNbvh6BKwNuh8Ai"
    )

    slack.send_message("general", text=str(sqs_messages))

    return {
        "statusCode": 200,
        "body": f"Message delivered to Slack: {str(sqs_messages)}",
    }
