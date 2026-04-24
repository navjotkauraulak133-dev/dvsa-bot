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
    app.run(host="0.0.0.0", port=10000)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DVSA_EMAIL = os.getenv("DVSA_EMAIL")
DVSA_PASSWORD = os.getenv("DVSA_PASSWORD")

CENTRES = ["Croydon", "Mitcham", "Bromley"]
CHECK_INTERVAL = 60

def send_alert(msg):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": msg}
    )

def run_bot():
    send_alert("✅ DVSA bot thread started")
    print("Starting DVSA bot...", flush=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print("Opening DVSA login page...", flush=True)
            page.goto("https://driverpracticaltest.dvsa.gov.uk/login", timeout=60000)

            print("Filling username...", flush=True)
            page.fill('input[name="username"]', DVSA_EMAIL)

            print("Filling password...", flush=True)
            page.fill('input[name="password"]', DVSA_PASSWORD)

            print("Clicking login...", flush=True)
            page.click('button[type="submit"]')

            print("Login clicked, waiting...", flush=True)
            page.wait_for_timeout(5000)

            while True:
                print("Checking centres...", flush=True)

                for centre in CENTRES:
                    print(f"Checking {centre}", flush=True)
                    time.sleep(2)

                time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("Error:", e, flush=True)

threading.Thread(target=run_bot, daemon=True).start()

run_web()
