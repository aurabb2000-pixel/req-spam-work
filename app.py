import os
import json
import requests
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)


def load_accounts(server):
    file_name = f"accounts-{server}.json"
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def send_via_thug_api(target_uid, account, results):
    try:
        
        token_url = f"https://jwt-generator-api-omega.vercel.app/api/token?uid={account['uid']}&password={account['password']}"
        token_res = requests.get(token_url, timeout=10)
        jwt_token = token_res.json().get('token')

        if jwt_token:
            
            thug_api_url = f"https://controle.thug4ff.com/send_requests?uid={target_uid}&token={jwt_token}"
            
            
            response = requests.get(thug_api_url, timeout=15)
            
            print(f"UID: {account['uid']} | Response: {response.text}")

           
            if response.status_code == 200:
                results["success"] += 1
            else:
                results["failed"] += 1
        else:
            results["failed"] += 1

    except Exception as e:
        print(f"Error for {account['uid']}: {e}")
        results["failed"] += 1


@app.route("/send", methods=["GET"])
def handle():
    target_uid = request.args.get("uid")
    server = request.args.get("server", "BD").upper()
    amount = int(request.args.get("amount", 10))

    if not target_uid:
        return jsonify({"error": "UID is missing"}), 400

    accounts = load_accounts(server)
    if not accounts:
        return jsonify({"error": "No accounts file found"}), 404

    results = {"success": 0, "failed": 0}
    threads = []
    
    
    for i in range(min(amount, len(accounts))):
        t = threading.Thread(target=send_via_thug_api, args=(target_uid, accounts[i], results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return jsonify({
        "status": "completed",
        "developer": "@TuutorSensi1",
        "target": target_uid,
        "success_count": results["success"],
        "failed_count": results["failed"]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)