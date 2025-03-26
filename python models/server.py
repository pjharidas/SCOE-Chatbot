from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# This function will be replaced by your custom logic
def process_message(message):
    # Placeholder function - replace with your own implementation
    return f"Echo: {message}"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Invalid request format. 'message' field is required"}), 400
        
        message = data['message']
        response = process_message(message)
        
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Server started on port 9090")
    app.run(host='0.0.0.0', port=9090, debug=True)