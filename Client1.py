from flask import Flask, Response, jsonify
import random
import time

app = Flask(__name__)

@app.route('/')
def index():
    return "Flask app running"

def generate_responses():
    with app.app_context():
        while True:
            
            rand_num = random.choice([0, 1, None])

           
            send_request = should_send_request()

            if send_request:
                response = {"data": rand_num}  
            else:
                response = {"data": None}  

            
            json_response = jsonify(response)
            
            response_bytes = json_response.data + b'\n'

            
            yield response_bytes

            
            time.sleep(1)

def should_send_request():
   
    intervals = [(0, 10), (10, 20), (20, 30)]  
    probabilities = [0.4, 0.5, 0.7] 
    
    
    current_time = time.time() % 30 
    
    
    for i, (start, end) in enumerate(intervals):
        if start <= current_time < end:
            
            return random.random() < probabilities[i]
    return False  

@app.route('/stream')
def stream():
    return Response(generate_responses(), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, port=5100)
