from flask import Flask, request, jsonify
import requests
import os
import base64
import json

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
        # Step 1: Username se UUID nikalna
        uuid_res = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if uuid_res.status_code != 200:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        user_data = uuid_res.json()
        uuid = user_data['id']
        actual_name = user_data['name']

        # Step 2: UUID se Profile Details aur Skin nikalna
        profile_res = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}")
        profile_data = profile_res.json()

        skin_url = "N/A"
        # Skin link Base64 encoded texture mein hota hai
        for prop in profile_data.get("properties", []):
            if prop["name"] == "textures":
                decoded_tex = json.loads(base64.b64decode(prop["value"]).decode("utf-8"))
                skin_url = decoded_tex.get("textures", {}).get("SKIN", {}).get("url")

        return jsonify({
            "status": "success",
            "result": {
                "username": actual_name,
                "uuid": uuid,
                "uuid_formatted": f"{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}",
                "skin_url": skin_url,
                "render_url": f"https://mc-heads.net/body/100/{uuid}", # Character render
                "avatar_url": f"https://mc-heads.net/avatar/100/{uuid}", # Face only
                "profile_link": f"https://namemc.com/profile/{uuid}"
            },
            "credits": {
                "api_by": "@Configexe",
                "source": "Mojang API"
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()
