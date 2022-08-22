import json
import boto3
import requests
import os
from datetime import datetime
import random

def lambda_handler(event, context):
    # TODO implement
    question = event['question']
    if (question != ""):
        tags = event['tags']
        id = str(random.randint(500000, 999999))
        
        url = os.getenv('ES_URL') + "posts/_doc"
        tagspl = [x.strip() for x in tags.split(',')]
        payload = {'id': id, 'tags': tagspl}
        print(payload)
        responseES = requests.post(url, auth=(os.getenv('ES_USER'), os.getenv('ES_PASS')), json=payload)
        print(responseES)
        client = boto3.client('dynamodb', region_name='us-east-1', aws_access_key_id=os.getenv('AWS_ACCESS'), aws_secret_access_key=os.getenv('AWS_SECRET'))
        currenttime = datetime.now().strftime('%Y-%d-%mT%H:%M:%S')
        payloadDB = {'id': {'S': id}, 'date': {'S': currenttime}, 'posts': {'S': question}}
        print(payloadDB)
        client.put_item(TableName='posts', Item=payloadDB)
        print(id)
        
    return json.dumps(question)
