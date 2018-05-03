#!flask/bin/python

import sys, glob

from flask import Flask, render_template, request, redirect, Response, jsonify
import random, json
import numpy as np
import boto3

app = Flask(__name__)

# AWS SQS INFO (I WILL TERMINATE THIS SQS SERVICE AFTER 05/03/2018 TO AVOID SERVICE FEES)
access_key = "AKIAJCTX5KSZCHFFW4YA"
access_secret = "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"
region ="us-east-1"
queue_url = "https://sqs.us-east-1.amazonaws.com/662429902571/hackathon"

# Use to Post message to AWS SQS for Alexa to interpret
def post_message(client, message_body, url):
    response = client.send_message(QueueUrl = url, MessageBody= message_body)

# Use to Check for messages on AWS SQS from Alexa. This is periodically called by main.js
def check_for_message(client, url, sleep_time = 2):
    
    response = client.receive_message(QueueUrl = url, MaxNumberOfMessages = 3, WaitTimeSeconds = 1)

    if 'Messages' in response:
        #last message posted becomes messages
        message = response['Messages'][0]['Body']
        receipt = response['Messages'][0]['ReceiptHandle']

        # Did Alexa indicate that we should start or stop recording?
        if (message == "Start") or (message == "Stop"):
            client.delete_message(QueueUrl = url, ReceiptHandle = receipt)
            print("GOT MESSAGE! - %s"%message)
            return message
        else:
            print("NO MSG, sleeping...")
            return False
    else:
        print("NO MSG, sleeping...")
        return False

# Now I use Flask to allow for Javascript and Python to talk to each other via AJAX requests
@app.route('/')
def output():
	# serve index template
	return render_template('index.html')

words_spoken = []
start_times = []
stop_times = []
client = boto3.client('sqs', aws_access_key_id = access_key, aws_secret_access_key = access_secret, region_name = region)

#This function parses all the JSON data sent to and from JS with AJAX
@app.route('/receiver', methods = ['POST'])
def receiver():
    # read json + reply
    global words_spoken, client, queue_url, start_times, stop_times

    jsondata = request.get_json()
    
    print(jsondata)

    if jsondata['type'] == "check_aws":
        message = check_for_message(client, queue_url)

        if message != False:
            if message == "Start":
                words_spoken = []
                start_times = []
                stop_times = []
            elif message == "Stop":
                print(words_spoken)
                print(start_times)
                print(stop_times)
                Run_Analytics()
            return jsonify(status="message", data=message)
        else:
            return jsonify(status="none", data="none")
    
    if jsondata['type'] == "words":
        words_spoken.append(jsondata['words'])
        start_times.append(float(jsondata['t0']))
        stop_times.append(float(jsondata['t1']))
        return jsonify(status="words", data="n/a")

    return jsonify(status="n/a", data="n/a")

# This is where the speech analytics occurs and gets posted to Alexa's feedback
def Run_Analytics():
    global start_times, stop_times, words_spoken, client, queue_url

    start_timesx = np.array(start_times)
    stop_timesx = np.array(stop_times)
    words_spokenx = np.array(words_spoken)

    pauses = start_timesx[1:] - stop_timesx[:-1]

    all_words = ""
    for sentense in words_spokenx:
        all_words += sentense+" "
    all_words = all_words.split(" ")

    num_of_words = np.array([len(x.split(" ")) for x in words_spokenx])

    filler_words = ['well', 'like', "okay", "ok", "right", "so"]
    filler_word_counts = []
    for word in filler_words:
        filler_word_counts.append(all_words.count(word))
        
    words_per_minute = num_of_words/(stop_timesx - start_timesx)*60

    avg_pause = np.round(np.mean(pauses),1)
    longest_pause = np.round(np.max(pauses),1)
    avg_wpm = np.round(np.mean(words_per_minute),1)

    total_filler_words = np.sum(filler_word_counts)
    #Generate Feedback

    summary = "Partap that was really good. You've improved a lot since last time. Here is what I noticed... "

    summary += "You use a total of %s filler words. "%total_filler_words
    summary += "Filler words such as like may seem natural in everyday speech, but they do not belong in formal presentations or speeches..."
    if total_filler_words > 2: # Give exact filler word count and feedback.
        for i in range(len(filler_word_counts)):
            if filler_word_counts[i] > 0:
                summary += "You used the word, %s, %s times. "%(filler_words[i], filler_word_counts[i])

    summary += "Having pauses in between statements is also a great way to control your pace, transition between ideas, and create dramatic contrast. "
    #Add context to why pausing is important
    summary += "In your case, you paused around %s seconds between statements, with the longest pause of %s seconds. "%(avg_pause, longest_pause)

    if longest_pause < 2:
        summary += "You might want to consider using more pauses for emphasis or build suspense. "
    
    summary += "Lastly, as for pacing, I did an analysis on 9 Ted talks and found that the average pace of speaking is between 120 and 170 words per minute. "
    summary += "I see that you spoke around %s words per minute..."%avg_wpm

    if avg_wpm > 170:
        summary += "Try to slow down your pacing and reduce below 170 words per minute. "
    elif avg_wpm < 120:
        summary += "Try to increase your pacing and target above 120 words per minute. "
    else:
        summary += "This is great pacing, keep it up!"
    
    #Send Message to Alexa
    print(summary)
    post_message(client, summary, queue_url)

    return

if __name__ == '__main__':
	# run!
	app.run()