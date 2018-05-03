import boto3
import time


# AWS SQS INFO (I WILL TERMINATE THIS SQS SERVICE AFTER 05/03/2018 TO AVOID SERVICE FEES)
access_key = "AKIAJCTX5KSZCHFFW4YA"
access_secret = "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"
region ="us-east-1"
queue_url = "https://sqs.us-east-1.amazonaws.com/662429902571/hackathon"

def wait_for_next_message(client, url, sleep_time = 2):
    

    response = client.receive_message(QueueUrl = url, MaxNumberOfMessages = 3, WaitTimeSeconds = 1)

    
    if 'Messages' in response:
        #last message posted becomes messages
        message = response['Messages'][0]['Body']
        receipt = response['Messages'][0]['ReceiptHandle']
        
        client.delete_message(QueueUrl = url, ReceiptHandle = receipt)
        
        return message
    else:
        return "I don't have any feedback yet... please have me listen again... or check back with me later."


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def post_message(client, message_body, url):
    response = client.send_message(QueueUrl = url, MessageBody= message_body)
    
default_introduction = "Hello, my name is Speak Buddy. I am here to listen to you and give feedback."
    
def lambda_handler(event, context):
    client = boto3.client('sqs', aws_access_key_id = access_key, aws_secret_access_key = access_secret, region_name = region)
    
    if event['request']['type'] == "LaunchRequest":
        speechlet = build_speechlet_response("Buddy Status", default_introduction, "", "true")
        return build_response({}, speechlet)
        
    intent_name = event['request']['intent']['name']
    
    if intent_name == "Start_Listening":
        post_message(client, 'Start', queue_url)
        speechlet = build_speechlet_response("Buddy Status", "Ok, I am listening", "", "true")
        return build_response({}, speechlet)
        
    elif intent_name == "Stop_Listening":
        post_message(client, 'Stop', queue_url)
        
        #wait_for_next_message(client, url, sleep_time = 2)
        
        #time.sleep(3)

        speechlet = build_speechlet_response("Buddy Status", "Ok I've stopped listening.", "", "true")

        return build_response({}, speechlet)
        
    elif intent_name == "Analyze":
        message = wait_for_next_message(client, queue_url, sleep_time = 2)
        speechlet = build_speechlet_response("Buddy Status", message, "", "true")

        return build_response({}, speechlet)
        
    else:
        message = "Unknown"
        
    speechlet = build_speechlet_response("Buddy Status", "I do not recognize that command", "", "true")
    return build_response({}, speechlet)