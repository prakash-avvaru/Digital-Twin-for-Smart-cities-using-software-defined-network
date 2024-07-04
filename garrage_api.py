from flask import Flask, request, jsonify
import pickle
import datetime
import pandas as pd
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load the models
with open('door_state.pkl', 'rb') as file:
    model1 = pickle.load(file)
with open('sphone_signal.pkl', 'rb') as file:
    model2 = pickle.load(file)
with open('Garage_label.pkl', 'rb') as file:
    model3 = pickle.load(file)

@app.route('/predict_garrage_status', methods=['POST','GET'])
def predict_garrage_status():
    try:
        # Extract date and time from the request
        # data = request.get_json(force=True)  # force=True helps to parse even if the mimetype is incorrect
        # logging.debug(f"Received data: {data}")
        
        system_datetime = request.args.get('dt') # "2024-05-01" #data.get('datetime')
        if not system_datetime:
            return jsonify({'error': 'Missing datetime in the request'}), 400

        # Convert string datetime to datetime object
        dt = datetime.datetime.fromisoformat(system_datetime)

        # Create a DataFrame with the necessary features
        features_df = pd.DataFrame({
            'month': [dt.month],
            'day': [dt.day],
            'hour': [dt.hour],
            'minute': [dt.minute]
        })

        # Make predictions using the models
        prediction_encoded_door_state = model1.predict(features_df).tolist()
        prediction_encoded_sphone_signal = model2.predict(features_df).tolist()
        prediction_encoded_garrage_label = model3.predict(features_df).tolist()
        
        # Return the prediction
        return jsonify({'door_state': prediction_encoded_door_state, 'sphone_signal': prediction_encoded_sphone_signal, 'garrage_label': prediction_encoded_garrage_label})

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
