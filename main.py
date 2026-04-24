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
    try:
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID, "text": msg}
        )
    except:
        print("Telegram failed", flush=True)

def run_bot():
    send_alert("✅ DVSA bot thread started")
    print("Starting DVSA bot...", flush=True)

    try:
        send_alert("1️⃣ Starting Playwright")

        with sync_playwright() as p:
            send_alert("2️⃣ Launching browser")
            browser = p.chromium.launch(headless=True)

            send_alert("3️⃣ Opening page")
            page = browser.new_page()

            send_alert("4️⃣ Opening DVSA login page")
            page.goto("https://driverpracticaltest.dvsa.gov.uk/login", timeout=60000)

            send_alert("5️⃣ Filling username")
            page.fill('input[name="username"]', DVSA_EMAIL)

            send_alert("6️⃣ Filling password")
            page.fill('input[name="password"]', DVSA_PASSWORD)

            send_alert("7️⃣ Clicking login")
            page.click('button[type="submit"]')

            send_alert("8️⃣ Waiting after login")
            page.wait_for_timeout(5000)

            send_alert("✅ Login step finished")

            while True:
                send_alert("🔁 Bot running...")
                time.sleep(60)

    except Exception as e:
        send_alert(f"❌ ERROR: {e}")
        print("Error:", e, flush=True)

threading.Thread(target=run_bot, daemon=True).start()

run_web()
