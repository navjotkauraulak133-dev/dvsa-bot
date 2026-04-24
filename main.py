from flask import Flask
import threading
import os
import time
import requests
import subprocess
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_alert(msg):
    try:
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
    except Exception as e:
        print("Telegram failed:", e, flush=True)

def run_bot():
    try:
        print("Installing Chromium...", flush=True)
        subprocess.run(
            ["python", "-m", "playwright", "install", "chromium"],
            check=True
        )

        send_alert("✅ DVSA bot started")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(
                "https://driverpracticaltest.dvsa.gov.uk/login",
                timeout=60000
            )

            send_alert("✅ DVSA page opened")

            while True:
                print("Bot running silently...", flush=True)
                time.sleep(180)

    except Exception as e:
        send_alert(f"❌ ERROR: {e}")
        print("Error:", e, flush=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    run_web()
