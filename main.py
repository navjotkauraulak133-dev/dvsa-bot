import os
import time
import requests
import subprocess
from playwright.sync_api import sync_playwright

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
    send_alert("✅ DVSA bot started")

    try:
        print("Installing browser...", flush=True)
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

            while True:
                print("Bot running silently...", flush=True)
                time.sleep(180)

    except Exception as e:
        send_alert(f"❌ ERROR: {e}")
        print("Error:", e, flush=True)

if __name__ == "__main__":
    run_bot()
