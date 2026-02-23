from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
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
        url = f"https://mcprofile.io/profile/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "Profile not found on website"}), 404

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Microsoft Account Information
        gamertag = username
        xuid = "N/A"
        account_tier = "N/A"
        gamescore = "0"

        # Website ke cards se data nikalna
        for card in soup.find_all("div", class_="card"):
            text = card.get_text()
            if "XUID" in text:
                xuid = text.replace("XUID", "").strip()
            if "Tier" in text:
                account_tier = text.replace("Tier", "").strip()
            if "Gamerscore" in text:
                gamescore = text.replace("Gamerscore", "").strip()

        # 2. GeyserMC Information
        geyser_linked = "No"
        floodgate_uuid = "N/A"
        
        # Check if Bedrock/Geyser
        if "Bedrock" in response.text or "Floodgate" in response.text:
            geyser_linked = "Yes"
            copy_btn = soup.find("button", {"data-clipboard-text": True})
            if copy_btn:
                floodgate_uuid = copy_btn["data-clipboard-text"]

        # 3. Skins & Visuals
        # mcprofile uses their own proxy or mc-heads
        skin_url = f"https://mc-heads.net/skin/{username}"
        avatar_url = f"https://mc-heads.net/avatar/100/{username}"

        return jsonify({
            "status": "success",
            "microsoft_account_info": {
                "gamertag": gamertag,
                "xuid": xuid,
                "account_tier": account_tier,
                "gamescore": gamescore
            },
            "geysermc_information": {
                "geyser_linked": geyser_linked,
                "skin_url": skin_url,
                "floodgate_uuid": floodgate_uuid
            },
            "visuals": {
                "avatar": avatar_url,
                "body_render": f"https://mc-heads.net/body/100/{username}"
            },
            "credits": {
                "api_by": "@Configexe",
                "source": "mcprofile.io Scraper"
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()
