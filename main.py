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

# 🔒 lock to prevent multiple threads
lock = threading.Lock()
bot_running = False

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
    global bot_running

    with lock:
        if bot_running:
            return
        bot_running = True

    print("Bot starting...", flush=True)
    send_alert("✅ DVSA bot started")

    try:
        # Install browser ONCE
        subprocess.run(
            ["python", "-m", "playwright", "install", "chromium"],
            check=True
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(
                "https://driverpracticaltest.dvsa.gov.uk/login",
                timeout=60000
            )

            send_alert("✅ DVSA page opened")

            # 🔁 LOOP (no spam)
            while True:
                time.sleep(120)  # every 2 mins

    except Exception as e:
        send_alert(f"❌ ERROR: {e}")
        print("Error:", e, flush=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    run_web()
