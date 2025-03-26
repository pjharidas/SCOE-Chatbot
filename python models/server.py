from flask import Flask, request, jsonify
import sys
import os
from chatbot2 import CollegeCounselorBot 

# Import the chatbot function from chatbot2.py
# Replace get_response with the actual function name if different

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    message = data['message']
    bot = CollegeCounselorBot("colleges.csv")
    # Call the chatbot function to get a response
    response = bot.get_response(message)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)