import time 
import pandas as pd 
import joblib
import requests
from datetime import datetime
from flask import *
import threading
import random 
from dotenv import load_dotenv
import os

import warnings
warnings.filterwarnings("ignore")


# Load environment variables from .env
load_dotenv()

def fetch_values():
    while True:
        time.sleep(5)
        try:
            # Create a datetime object (replace with your desired date and time)
            dd=random.randint(1,28)
            mm=random.randint(1,12)
            yy=random.randint(2022,2024)
            hh=random.randint(0,23)
            mi=random.randint(0,59)
            ss=random.randint(0,59)
            date_time = datetime(yy, mm, dd, hh, mi, ss)  # Year, Month, Day, Hour, Minute
            # Format the datetime object as a string (adjust format if needed)
            date_time_str = date_time.strftime("%Y-%m-%dT%H:%M:%SZ")  # ISO 8601 format
            # Prepare the data to send (adjust key names if needed)
            data = {"date_time": date_time_str}
            # Send POST request to the API
            response = requests.post(api_url+date_time_str, json=data)
            # Check for successful response
            if response.status_code == 200:
                # Get the response data (assuming JSON format)
                result = response.json()
                print(result)
                #print(dd)
                #print(mm)
                data = [dd,mm,10,0,result['door_state'][0], result['garrage_label'][0], result['sphone_signal'][0]]
                predictions = model.predict([data])
                print("Predicted type of attack:", predictions[0])
                if predictions[0]==3:
                    try:
                        print('sending alert to other network ...')
                        response = requests.post(other_network_url, json={"attacktype":str(predictions[0])})
                        print('response...',str(response))
                    except Exception as exp:
                        print('other network issue ', exp)
                print("API result:", result)
            else:
                print("Error:", response.status_code, response.text)
        except Exception as exp:
            print('thread issue ', exp)    
        #return "ok"

api_url = "http://127.0.0.1:5000/predict_garrage_status?dt="
model = joblib.load('Garage_model.joblib')
other_network_url = os.getenv("other_network_url")

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    return "ok"

@app.route('/receiveAlert', methods=['GET', 'POST'])
def receiveAlert():
    print('...received from network', str(request.data))
    # get alert info 
    # 
    return "alert info received . tq"+str(request.data) 

fetch_thread = threading.Thread(target=fetch_values)
fetch_thread.start()
app.run(use_reloader=False, port=6000, host="0.0.0.0")
        
