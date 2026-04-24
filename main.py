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

# 🔒 Prevent multiple runs
bot_started = False

def run_bot():
    global bot_started
    if bot_started:
        return
    bot_started = True

    try:
        send_alert("✅ DVSA checker started")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            send_alert("Opening DVSA login page")

            page.goto(
                "https://driverpracticaltest.dvsa.gov.uk/login",
                timeout=60000
            )

            send_alert("✅ DVSA page opened")

            while True:
                print("Bot running...", flush=True)
                time.sleep(180)

    except Exception as e:
        send_alert(f"❌ ERROR: {e}")
        print("Error:", e, flush=True)

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()
