import json
import os
import requests
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Get the message from the request
            message = data.get('message')
            if not message:
                self.send_json_response(400, {'error': 'Message is required'})
                return
            
            # Get Claude API key from environment variables
            api_key = os.environ.get('CLAUDE_API_KEY')
            if not api_key:
                self.send_json_response(500, {'error': 'API key not configured'})
                return
            
            # Call Claude API
            claude_text = self.call_claude_api(api_key, message)
            
            if claude_text:
                # Send successful response
                self.send_json_response(200, {'response': claude_text})
            else:
                self.send_json_response(500, {'error': 'Failed to get response from Claude'})
                
        except Exception as e:
            print(f"Error: {str(e)}")
            self.send_json_response(500, {'error': f'Internal server error: {str(e)}'})
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def call_claude_api(self, api_key, message):
        try:
            url = 'https://api.anthropic.com/v1/messages'
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01'
            }
            
            payload = {
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 1000,
                'messages': [{'role': 'user', 'content': message}],
                'tools':[
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": 3
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data['content'][0]['text']
            else:
                print(f"Claude API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling Claude API: {str(e)}")
            return None
    
    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        json_data = json.dumps(data)
        self.wfile.write(json_data.encode('utf-8'))