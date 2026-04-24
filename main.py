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
DVSA_EMAIL = os.getenv("DVSA_EMAIL")
DVSA_PASSWORD = os.getenv("DVSA_PASSWORD")

bot_started = False

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
    global bot_started

    if bot_started:
        return

    bot_started = True
    send_alert("✅ DVSA bot thread started")

    try:
        send_alert("Installing Playwright browser...")
        subprocess.run(
            ["python", "-m", "playwright", "install", "chromium"],
            check=True
        )
        send_alert("Browser installed")

        send_alert("1️⃣ Starting Playwright")

        with sync_playwright() as p:
            send_alert("2️⃣ Launching browser")
            browser = p.chromium.launch(headless=True)

            send_alert("3️⃣ Opening page")
            page = browser.new_page()

            send_alert("4️⃣ Opening DVSA login page")
            page.goto(
                "https://driverpracticaltest.dvsa.gov.uk/login",
                timeout=60000
            )

            send_alert("5️⃣ DVSA page opened")

            while True:
                send_alert("🔁 Bot running...")
                time.sleep(60)

    except Exception as e:
        send_alert(f"❌ ERROR: {e}")
        print("Error:", e, flush=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    run_web()
