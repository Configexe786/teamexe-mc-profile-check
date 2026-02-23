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
        # mcprofile.io uses this structure to show both Java/Bedrock
        url = f"https://mcprofile.io/profile/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "User not found on mcprofile.io"}), 404

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting data from the page 
        # Website usually stores UUID in a meta tag or a specific class
        uuid = "N/A"
        uuid_tag = soup.find("button", {"data-clipboard-text": True})
        if uuid_tag:
            uuid = uuid_tag["data-clipboard-text"]

        # Skin and Avatar logic
        # mcprofile uses mc-heads or their own cdn for renders
        avatar_url = f"https://mc-heads.net/avatar/100/{username}"
        body_render = f"https://mc-heads.net/body/100/{username}"
        skin_url = f"https://mc-heads.net/skin/{username}"

        # Check if it's Bedrock (mcprofile usually marks this)
        is_bedrock = False
        if "Bedrock" in response.text or username.startswith('.'):
            is_bedrock = True

        return jsonify({
            "status": "success",
            "type": "Bedrock" if is_bedrock else "Java",
            "result": {
                "username": username,
                "uuid": uuid,
                "skin_url": skin_url,
                "avatar": avatar_url,
                "body_render": body_render,
                "profile_link": url
            },
            "credits": {
                "api_by": "@Configexe",
                "source": "mcprofile.io"
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()
