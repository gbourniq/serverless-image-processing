""" Manage secret in AWS Secrets Manager/slscrypt/environment. """
import base64
import os

import boto3

try:
    import slscrypt

    RUNNING_ON_LAMBDA = True
except ImportError:
    RUNNING_ON_LAMBDA = False


def get_secret(secret_name, region_name="us-east-1"):
    """ Retrieve secret_name from supplied region. Returns the secret. """
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in get_secret_value_response:
        secret = get_secret_value_response["SecretString"]
    else:
        secret = base64.b64decode(get_secret_value_response["SecretBinary"])

    return secret


def get_secret_or_environment(secret_name):
    """ Gets encrypted value from slscrypt if on Lambda, or local
      environment variable otherwise.

      Parameters:
        - secret_name - the secret to fetch

      Returns:
        - the secret
  """
    if RUNNING_ON_LAMBDA:
        return slscrypt.get(secret_name)
    return os.environ[secret_name]
