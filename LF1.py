import json
import boto3
import requests
import os

def lambda_handler(event, context):
    input = event['queryStringParameters']['q'].strip()
    email = event['queryStringParameters']['email'].strip()
    
    client = boto3.client('lex-runtime')
    responseLex = client.post_text(botName="GetAnswer", botAlias="answerIntent", userId=os.getenv('ACCOUNT_ID'), inputText=input)
    if 'slots' in responseLex:
        url = os.getenv('ES_URL') + "posts/_search?q=" + responseLex['slots']['slotOne'].lower()
        if (responseLex['slots']['slotTwo'] != None and responseLex['slots']['slotTwo'] != ""):
            url += " OR " + response['slots']['slotTwo'].lower()
            
        responseES = requests.get(url, auth=(os.getenv('ES_USER'), os.getenv('ES_PASS')))
        r = responseES.json()
        
        idList = []
        if 'hits' in r:
            count = 0
            for val in r['hits']['hits']:
                idList.append(val['_source']['id'])
                count += 1
                if count == 3:
                    break
        
            client = boto3.client('dynamodb', region_name='us-east-1', aws_access_key_id=os.getenv('AWS_ACCESS'), aws_secret_access_key=os.getenv('AWS_SECRET'))
            answerList = []
            for id in idList:
                payload = {'id': {'S': id}}
                responseDB = client.get_item(TableName='posts', Key=payload)
                answerList.append(responseDB['Item'])
            
            clientSES = boto3.client('ses')
            body = "<html>"
            for answer in answerList:
                body += answer['date']['S'] + "<br>" + answer['posts']['S'] + "<br><br>"
            body += "</html>"
            email_message = { 'Body': { 'Html': { 'Charset': 'utf-8', 'Data': body } }, 'Subject': { 'Charset': 'utf-8', 'Data': "Search Results"} }
            
            responseSES = clientSES.send_email(Destination = { 'ToAddresses': [email] }, Message=email_message, Source="gavinjsenger@gmail.com")
            return {
                'statusCode': 200,
                'body': json.dumps(answerList)
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps([])
            }
            
    else:
        return {
            'statusCode': 200,
            'body': json.dumps([])
        }
