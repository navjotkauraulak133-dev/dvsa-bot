import os
import time
import requests
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
        print("Telegram failed:", e)

def run_bot():
    print("Bot starting...", flush=True)
    send_alert("✅ DVSA bot started")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://driverpracticaltest.dvsa.gov.uk/login")

        send_alert("✅ DVSA page opened")

        while True:
            time.sleep(180)  # no spam

if __name__ == "__main__":
    run_bot()
