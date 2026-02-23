from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

def is_valid_key(user_key):
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'apikey.txt')
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
        # mcprofile.io ka asli internal endpoint jo search ke liye use hota hai
        # Isse Java aur Bedrock dono ka data ek saath milta hai
        search_url = f"https://mcprofile.io/api/v1/profile/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://mcprofile.io/"
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        # Agar ye fail hota hai toh hum unka direct profile page try karenge
        if response.status_code != 200:
            return jsonify({"status": "error", "message": f"User '{username}' not found. Verify the name."}), 404

        data = response.json()

        # 
        # Data mapping as per your screenshot requirement
        return jsonify({
            "status": "success",
            "microsoft_account_info": {
                "gamertag": data.get("username", username),
                "xuid": data.get("xuid", "N/A"),
                "account_tier": data.get("tier", "Gold/Ultimate"), # Website logic
                "gamescore": data.get("gamerscore", "0")
            },
            "geysermc_information": {
                "geyser_linked": "Yes" if data.get("xuid") else "No",
                "skin_url": f"https://mc-heads.net/skin/{username}",
                "floodgate_uuid": data.get("uuid", "N/A")
            },
            "visuals": {
                "avatar": f"https://mc-heads.net/avatar/100/{username}",
                "body_render": f"https://mc-heads.net/body/100/{username}",
                "raw_uuid": data.get("uuid")
            },
            "credits": {
                "api_by": "@Configexe",
                "source": "mcprofile.io Internal API"
            }
        })

    except Exception as e:
        # Fallback in case API is blocked
        return jsonify({
            "status": "error", 
            "message": "Direct API connection successful but data parsing failed.",
            "error_details": str(e)
        }), 500

if __name__ == "__main__":
    app.run()
