from flask import Flask
import threading
import os
import time
import requests
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
print("MAIN.PY STARTED", flush=True)

requests.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    params={"chat_id": CHAT_ID, "text": "✅ Render bot started"},
    timeout=10
)
DVSA_EMAIL = os.getenv("DVSA_EMAIL")
DVSA_PASSWORD = os.getenv("DVSA_PASSWORD")

CENTRES = ["Croydon", "Mitcham", "Bromley"]
CHECK_INTERVAL = 60

def send_alert(msg):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": msg},
        timeout=10
    )

def run_bot():
    try:
        print("Starting DVSA bot...", flush=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print("Trying DVSA login now...", flush=True)
            page.goto("https://driverpracticaltest.dvsa.gov.uk/login")

            page.fill('input[name="username"]', DVSA_EMAIL)
            page.fill('input[name="password"]', DVSA_PASSWORD)
            page.click('button[type="submit"]')

            page.wait_for_timeout(5000)

            while True:
                print("Checking DVSA now...", flush=True)

                for centre in CENTRES:
                    print(f"Checking {centre}", flush=True)
                    time.sleep(2)

                time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print(f"BOT ERROR: {e}", flush=True)

threading.Thread(target=run_bot, daemon=True).start()

run_web()
