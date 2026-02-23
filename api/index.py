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
        # Step 1: Java (Mojang) Check
        mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        mojang_res = requests.get(mojang_url, timeout=5)
        
        if mojang_res.status_code == 200:
            data = mojang_res.json()
            uuid = data['id']
            return jsonify({
                "status": "success",
                "type": "Java",
                "result": {
                    "username": data['name'],
                    "uuid": uuid,
                    "avatar": f"https://mc-heads.net/avatar/100/{uuid}",
                    "body": f"https://mc-heads.net/body/100/{uuid}",
                    "skin": f"https://mc-heads.net/skin/{uuid}",
                    "profile_link": f"https://mcprofile.io/profile/{username}"
                },
                "credits": {"api_by": "@Configexe"}
            })

        # Step 2: Bedrock Check (mcprofile.io & Geyser Logic)
        # Bedrock profiles ko fetch karne ke liye hume XUID ya Floodgate ID chahiye hoti hai
        bedrock_url = f"https://api.geyserconnect.net/v2/xbox/gamertag/{username}"
        bedrock_res = requests.get(bedrock_url, timeout=5)

        if bedrock_res.status_code == 200:
            data = bedrock_res.json()
            xuid = str(data.get('xuid'))
            # Floodgate UUID format for Bedrock
            f_uuid = f"00000000-0000-0000-0000-{int(xuid):012x}"
            
            return jsonify({
                "status": "success",
                "type": "Bedrock",
                "result": {
                    "username": data.get('gamertag'),
                    "xuid": xuid,
                    "uuid": f_uuid,
                    "avatar": f"https://mc-heads.net/avatar/100/{username}",
                    "body": f"https://mc-heads.net/body/100/{username}",
                    "skin": f"https://mc-heads.net/skin/{username}",
                    "profile_link": f"https://mcprofile.io/profile/{username}"
                },
                "credits": {"api_by": "@Configexe"}
            })
        
        return jsonify({"status": "error", "message": "User not found on Java or Bedrock databases."}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": "API Connection Timeout", "details": str(e)}), 500

if __name__ == "__main__":
    app.run()
