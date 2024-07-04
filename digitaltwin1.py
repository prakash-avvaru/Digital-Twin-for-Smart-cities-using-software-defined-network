import time 
import pandas as pd 
import joblib
import requests
from datetime import datetime

# Define your API endpoint URL (replace with the actual URL)
api_url = "http://127.0.0.1:5000/predict_garrage_status?dt="

model = joblib.load('Garage_model.joblib')

import random 
#df = pd.read_csv('Train_Test_IoT_Garage_Door.csv')
while True:
    time.sleep(5)
    # Create a datetime object (replace with your desired date and time)
    dd=random.randint(1,28)
    mm=random.randint(1,12)
    yy=random.randint(2022,2024)
    date_time = datetime(yy, mm, dd, 10, 0, 0)  # Year, Month, Day, Hour, Minute

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
        print(dd)
        print(mm)
        data = [dd,mm,10,0,result['door_state'][0], result['garrage_label'][0], result['sphone_signal'][0]]
        predictions = model.predict([data])
        print("Predicted type of attack:", predictions[0])


        print("API result:", result)



    else:
        print("Error:", response.status_code, response.text)
        
