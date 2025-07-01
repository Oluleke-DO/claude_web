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
                self.send_error_response(400, 'Message is required')
                return
            
            # Get Claude API key from environment variables
            api_key = os.environ.get('CLAUDE_API_KEY')
            if not api_key:
                self.send_error_response(500, 'API key not configured')
                return
            
            # Call Claude API
            claude_response = self.call_claude_api(api_key, message)
            
            if claude_response:
                # Send successful response
                self.send_success_response({'response feedback': claude_response})
            else:
                self.send_error_response(500, 'Failed to get response from Claude')
                
        except json.JSONDecodeError:
            self.send_error_response(400, 'Invalid JSON in request body')
        except Exception as e:
            print(f"Error: {str(e)}")
            self.send_error_response(500, f'Internal server error: {str(e)}')
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_cors_headers()
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
                'model': 'claude-3-5-haiku-20241022',  # Change to claude-3-haiku-20240307  'for cheaper
                'max_tokens': 1000,
                'messages': [
                    {
                        'role': 'user',
                        'content': message
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
                
        except requests.exceptions.Timeout:
            print("Request to Claude API timed out")
            return None
        except Exception as e:
            print(f"Error calling Claude API: {str(e)}")
            return None
    
    def send_success_response(self, data):
        self.send_response(200)
        self.send_cors_headers()
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_cors_headers()
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())
    
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')