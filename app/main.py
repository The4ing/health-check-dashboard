from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

# רשימת אתרים לבדיקה
sites = [
    "https://google.com",
    "https://cyberark.com",
    "https://github.com"
]

@app.route("/")
def health_check():
    results = []
    for site in sites:
        start = time.time()
        try:
            r = requests.get(site, timeout=5)
            status = "UP" if r.status_code == 200 else "DOWN"
        except Exception:
            status = "DOWN"
        response_time = round((time.time() - start) * 1000, 2)
        results.append({"site": site, "status": status, "response_time_ms": response_time})
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
