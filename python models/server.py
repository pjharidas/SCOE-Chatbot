from flask import Flask, request, jsonify
from flask_cors import CORS  # Import Flask-CORS
import chatbot3  # Use the new chatbot module

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    message = data['message']
    # Use the chatbot function from chatbot3 to process the query.
    response = chatbot3.process_user_query(message)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
