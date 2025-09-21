"""
Trigger script that simply sends a request to the server every few minutes.
When the server receives a request from this Lambda function, it pushes all
the pages it has to an SQS queue for a different Lambda function to pick up.
"""

import os
import requests


is_lambda = "AWS_LAMBDA_FUNCTION_NAME" in os.environ

if is_lambda:
    SERVER_URL = 'https://jobs.hrus.in'
else:
    SERVER_URL = 'http://127.0.0.1:8000'


def lambda_handler(event, context):
    # Just send a request to our server with the API key in the header
    requests.get(SERVER_URL + '/api/pages/list', headers={'X-API-Key': os.environ.get('HAWK_API_KEY', '')})
