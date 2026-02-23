from flask import Flask, request, jsonify
import requests
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
        # mcprofile.io ki internal API jo seedha details deti hai
        # Hum wahi headers bhejenge jo unka dashboard bhejta hai
        api_url = f"https://mcprofile.io/api/v1/profile/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": f"https://mcprofile.io/profile/{username}"
        }

        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "User not found on mcprofile.io"}), 404

        data = response.json()

        # Saara data jo aapne screenshots me dikhaya hai
        return jsonify({
            "status": "success",
            "microsoft_account_info": {
                "gamertag": data.get("username", username),
                "xuid": data.get("xuid", "N/A"),
                "account_tier": data.get("tier", "N/A"),
                "gamescore": data.get("gamerscore", "0")
            },
            "geysermc_information": {
                "geyser_linked": "true" if data.get("is_geyser") else "false",
                "skin_url": f"https://mcprofile.io/api/v1/skin/render/body/{username}", # Direct from their server
                "floodgate_uuid": data.get("uuid", "N/A")
            },
            "visuals": {
                "avatar": f"https://mcprofile.io/api/v1/skin/render/avatar/{username}",
                "full_body": f"https://mcprofile.io/api/v1/skin/render/body/{username}"
            },
            "credits": {
                "api_by": "@Configexe",
                "source": "mcprofile.io"
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": "Connection error with mcprofile.io", "details": str(e)}), 500

if __name__ == "__main__":
    app.run()
