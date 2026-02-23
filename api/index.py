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
        # Step 1: Pehle Java (Mojang) check karte hain
        mojang_res = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        
        if mojang_res.status_code == 200:
            # JAVA USER FOUND
            data = mojang_res.json()
            uuid = data['id']
            return jsonify({
                "status": "success",
                "type": "Java",
                "result": {
                    "username": data['name'],
                    "uuid": uuid,
                    "skin_url": f"https://mc-heads.net/skin/{uuid}",
                    "body_render": f"https://mc-heads.net/body/100/{uuid}",
                    "avatar": f"https://mc-heads.net/avatar/100/{uuid}",
                    "profile_at": f"https://namemc.com/profile/{username}"
                },
                "credits": {"api_by": "@Configexe"}
            })
        
        else:
            # Step 2: Agar Java nahi mila, toh Bedrock check karte hain (Geyser/Floodgate logic)
            # Bedrock usernames usually start with '.' on many servers, but API uses XUID
            # Hum mcprofile.io ki internal helper API use karenge
            bedrock_res = requests.get(f"https://api.geyserconnect.net/v2/xbox/gamertag/{username}")
            
            if bedrock_res.status_code == 200:
                data = bedrock_res.json()
                xuid = str(data.get('xuid'))
                return jsonify({
                    "status": "success",
                    "type": "Bedrock",
                    "result": {
                        "username": data.get('gamertag'),
                        "xuid": xuid,
                        "floodgate_id": f"00000000-0000-0000-000{hex(int(xuid))[2:]}",
                        "avatar": f"https://mc-heads.net/avatar/100/{username}",
                        "skin_url": "Bedrock skins are managed via Xbox Live",
                        "note": "Use XUID for bedrock specific tools"
                    },
                    "credits": {"api_by": "@Configexe"}
                })
            else:
                return jsonify({"status": "error", "message": "User not found on Java or Bedrock"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()
