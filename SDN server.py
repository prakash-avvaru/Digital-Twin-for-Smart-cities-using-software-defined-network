import time 
import requests
from datetime import datetime
from flask import Flask, request
import threading
import random 
from dotenv import load_dotenv
import os

import warnings
warnings.filterwarnings("ignore")


load_dotenv()


url_api1 = 'http://localhost:5100/stream'
url_api2 = 'http://localhost:5500/stream'
other_network_url = 'http://localhost:5000/receiveAlert'
blacklisted_apis = set()


def reset_count():
    global count_api1, count_api2, total_count
    count_api1 = 0
    count_api2 = 0
    total_count = 0


def start_timer():
    while True:
        start_time = time.time()
        count_api1 = 0  
        count_api2 = 0  
        total_count = 0  

        
        while time.time() - start_time < 30:
            with requests.Session() as session:
                try:
                    response_api1 = session.get(url_api1, stream=True) if url_api1 not in blacklisted_apis else None
                    response_api2 = session.get(url_api2, stream=True) if url_api2 not in blacklisted_apis else None
                    iteration = 0
                    for response_api1_line, response_api2_line in zip(response_api1.iter_lines(), response_api2.iter_lines()) if response_api1 and response_api2 else []:
                        if response_api1_line and response_api2_line:
                            # Extract the values of the "data" key
                            split_response1 = response_api1_line.strip().split(b':')
                            split_response2 = response_api2_line.strip().split(b':')

                            
                            if len(split_response1) >= 2 and len(split_response2) >= 2:
                                value_api1 = split_response1[1].strip() if url_api1 not in blacklisted_apis else b'null'
                                value_api2 = split_response2[1].strip() if url_api2 not in blacklisted_apis else b'null'

                                # Check if both values are not null
                                if value_api1 != b'null':
                                    count_api1 += 1
                                if value_api2 != b'null':
                                    count_api2 += 1
                                if value_api1 != b'null' and value_api2 != b'null':
                                    total_count += 1
                        iteration += 1
                        if iteration % 120 == 0:
                            print("Count Change in last 30 iterations:")
                            print("API 1 count:", count_api1)
                            print("API 2 count:", count_api2)
                            print("Total count:", total_count)

                            if total_count > 5:
                                if count_api1 > count_api2:
                                    print("DDOS detected API 1 is blacklisted.")
                                    blacklisted_apis.add(url_api1)
                                    # Send message to other network URL
                                    send_message_to_other_network("DDOS detected API 1 is blacklisted.")
                                else:
                                    print("DDOS detected API 2 is blacklisted.")
                                    blacklisted_apis.add(url_api2)
                                    # Send message to other network URL
                                    send_message_to_other_network("DDOS detected API 2 is blacklisted.")
                            count_api1 = 0
                            count_api2 = 0
                            total_count = 0
                except requests.RequestException as e:
                    print("Error fetching data:", e)
            reset_count()  # Reset count after each 15 seconds
            print("Timer reset. Counts after 15 seconds:")
            print("API 1 count:", count_api1)
            print("API 2 count:", count_api2)
            print("Total count:", total_count)

def send_message_to_other_network(message):
    try:
        response = requests.post(other_network_url, data=message)
        if response.status_code == 200:
            print("Message sent to other network successfully.")
        else:
            print("Failed to send message to other network. Status code:", response.status_code)
    except requests.RequestException as e:
        print("Error sending message to other network:", e)

# Start the timer
start_timer()


app = Flask(__name__)

@app.route('/receiveAlert', methods=['GET', 'POST'])
def receiveAlert():
    if request.method == 'POST':
        print('Received POST request from network:', request.data)
        
    elif request.method == 'GET':
        print('Received GET request from network:', request.args)
        
    return "Alert info received. Thank you."

@app.route('/receiveMessageFromOtherNetwork', methods=['POST'])
def receiveMessageFromOtherNetwork():
    if request.method == 'POST':
        message = request.data
        print('Received message from other network:', message)
        
    return "Message received from other network."

if __name__ == "__main__":
    app.run(debug=True)  
