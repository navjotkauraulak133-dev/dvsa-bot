from flask import Flask
import threading
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
        send_alert("✅ DVSA checker started")

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)

        send_alert("Opening DVSA login page")
        driver.get("https://driverpracticaltest.dvsa.gov.uk/login")

        send_alert("✅ DVSA page opened")

        while True:
            print("Bot running...", flush=True)
            time.sleep(180)

    except Exception as e:
        send_alert(f"❌ ERROR: {e}")
        print("Error:", e, flush=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    run_web()
