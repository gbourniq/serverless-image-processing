# Serverless Sample Project

Prerequisites
* conda
* poetry
* node: `brew upgrade node`
* serverless: `npm install -g serverless`



# Use Serverless Dashboard to store AWS credentials
1. Create an `serverless-admin` AWS user with `admin` permissions and programatic access for serverless
2. Access the Serverless Dashboard via the `serverless login` command, and configure an AWS provider to store the user credentials.
3. Create an application in the serverless dashboard
4. Populalate the following section in `serverless.yml`
```
org: <serverless account name>
app: <app name>
service: <service name>
```

# Use SSM Parameter Store to manage Secrets

```bash
aws ssm put-parameter --name SLACK_API_TOKEN --value <slack api token value> --type "SecureString" --overwrite
```