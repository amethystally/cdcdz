from http.server import BaseHTTPRequestHandler
import json
import requests
import re
import urllib.parse
from bs4 import BeautifulSoup

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        # Get the username from the request
        username = data.get('username', '')
        
        # Call the TikTok analysis function
        result = get_user_info(username)
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Convert result to JSON and send
        self.wfile.write(json.dumps(result).encode())
        return
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return

def get_user_info(identifier, by_id=False):
    # Remove the @ symbol if present
    if identifier.startswith('@'):
        identifier = identifier[1:]
    # URL for username
    url = f"https://www.tiktok.com/@{identifier}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Try to use lxml parser if available, otherwise use html.parser
            try:
                soup = BeautifulSoup(html_content, 'lxml')
            except:
                soup = BeautifulSoup(html_content, 'html.parser')
            
            # Regular expressions to extract information
            patterns = {
                'user_id': r'"webapp.user-detail":{"userInfo":{"user":{"id":"(\d+)"',
                'unique_id': r'"uniqueId":"(.*?)"',
                'nickname': r'"nickname":"(.*?)"',
                'followers': r'"followerCount":(\d+)',
                'following': r'"followingCount":(\d+)',
                'likes': r'"heartCount":(\d+)',
                'videos': r'"videoCount":(\d+)',
                'signature': r'"signature":"(.*?)"',
                'verified': r'"verified":(true|false)',
                'privateAccount': r'"privateAccount":(true|false)',
                'region': r'"region":"(.*?)"',
            }
            
            # Extract information using the defined patterns
            info = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, html_content)
                info[key] = match.group(1) if match else f"No {key} found"
            
            return info
        else:
            return {"error": f"Unable to fetch profile. Status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}