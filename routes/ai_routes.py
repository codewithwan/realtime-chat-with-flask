from flask import Blueprint, request, jsonify
import requests
import json
import os

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ask', methods=['POST'])
def ask_ai():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'error': 'Question is required'}), 400

    url = 'https://xiex.my.id/api/ai/chat/completions'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'apikey': os.getenv('API_KEY'),
        'model': 'brainxiex',
        'server': 1,
        'messages': [{'role': 'user', 'content': question}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return jsonify({'answer': response.json().get('answer')})
    else:
        return jsonify({'error': 'Failed to get response from AI service'}), 500