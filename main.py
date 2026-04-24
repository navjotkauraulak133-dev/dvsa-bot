from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()
import os
import time
import requests
from playwright.sync_api import sync_playwright
import os
os.system("playwright install chromium")
print("Chromium installed, starting bot...", flush=True)

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

print("Trying DVSA login now...", flush=True)
def login(page):
    page.goto("https://driverpracticaltest.dvsa.gov.uk/login")

    page.fill('input[name="username"]', DVSA_EMAIL)
    page.fill('input[name="password"]', DVSA_PASSWORD)
    page.click('button[type="submit"]')

    page.wait_for_timeout(5000)

    page.click("text=Change your test")
    page.wait_for_timeout(3000)

    page.click("text=Find an earlier test")
    page.wait_for_timeout(5000)

def fetch_slots(page, centre):
    slots = []

    page.fill('input[name="testCentre"]', centre)
    page.click("text=Search")

    page.wait_for_timeout(4000)

    elements = page.locator(".SlotPicker-slotDate")

    for i in range(elements.count()):
        slots.append(elements.nth(i).inner_text())

    return slots

def format_msg(data):
    if not data:
        return None

    msg = "🚨 DVSA Cancellations:\n\n"

    for centre, slots in data.items():
        msg += f"📍 {centre}\n"
        for s in slots[:5]:
            msg += f" - {s}\n"
        msg += "\n"

    msg += "👉 Book now:\nhttps://driverpracticaltest.dvsa.gov.uk/login"

    return msg


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    login(page)

    last_msg = None

    while True:
        try:
            results = {}

            for centre in CENTRES:
                slots = fetch_slots(page, centre)
                if slots:
                    results[centre] = slots

                time.sleep(5)

            msg = format_msg(results)

            if msg and msg != last_msg:
                send_alert(msg)
                last_msg = msg

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print("Error:", e)
            login(page)
