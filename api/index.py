from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

def is_valid_key(user_key):
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'apikey.txt')
        if not os.path.exists(file_path): return False
        with open(file_path, 'r') as f:
            return user_key in [line.strip() for line in f.readlines()]
    except: return False

@app.route('/mc-profile', methods=['GET'])
def get_mc_profile():
    username = request.args.get('username')
    api_key = request.args.get('key')

    if not api_key or not is_valid_key(api_key):
        return jsonify({"status": "error", "message": "Invalid API Key"}), 403

    if not username:
        return jsonify({"status": "error", "message": "Username is required"}), 400

    try:
        url = f"https://mcprofile.io/profile/{username}"
        # Professional Headers taaki block na ho
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return jsonify({"status": "error", "message": f"User '{username}' not found on any database."}), 404

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. UUID find karne ka solid tarika
        uuid = "N/A"
        copy_btn = soup.find("button", {"data-clipboard-text": True})
        if copy_btn:
            uuid = copy_btn["data-clipboard-text"]

        # 2. Type find karna (Java ya Bedrock)
        is_bedrock = False
        badge = soup.find("span", string=lambda x: x and "Bedrock" in x)
        if badge or username.startswith('.'):
            is_bedrock = True

        # 3. Image URLs (mcprofile.io uses mc-heads logic)
        clean_user = username.replace('.', '') if is_bedrock else username
        
        return jsonify({
            "status": "success",
            "type": "Bedrock" if is_bedrock else "Java",
            "result": {
                "username": username,
                "uuid": uuid,
                "avatar": f"https://mc-heads.net/avatar/100/{username}",
                "body_render": f"https://mc-heads.net/body/100/{username}",
                "skin_texture": f"https://mc-heads.net/skin/{username}",
                "mcprofile_url": url
            },
            "credits": {
                "api_by": "@Configexe",
                "source": "mcprofile.io"
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": "System Overloaded or Scraping Failed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run()
