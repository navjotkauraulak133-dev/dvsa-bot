from flask import Flask
import threading, os, time, requests, subprocess
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
LICENCE = os.getenv("DVSA_LICENCE")
BOOKING = os.getenv("DVSA_BOOKING")

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
        subprocess.run(
            ["python", "-m", "playwright", "install", "chromium"],
            check=True
        )

        if not LICENCE or not BOOKING:
            raise ValueError("DVSA_LICENCE or DVSA_BOOKING missing")

        send_alert("🚀 DVSA bot started")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )

            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
            )

            while True:
                try:
                    print("Checking DVSA...", flush=True)

                    page.goto(
                        "https://driverpracticaltest.dvsa.gov.uk/login",
                        timeout=60000
                    )

                    page.wait_for_timeout(10000)

                    html = page.content()

                    if "driving-licence-number" not in html:
                        send_alert("❌ DVSA blocked or page not loaded")
                        time.sleep(120)
                        continue

                    page.fill("#driving-licence-number", LICENCE)
                    page.fill("#booking-reference", BOOKING)

                    page.click("button[type=submit]")
                    page.wait_for_timeout(7000)

                    content = page.content()

                    if "No tests available" not in content:
                        send_alert("🔥 POSSIBLE SLOT FOUND! Check DVSA now.")
                    else:
                        print("No slots found", flush=True)

                    time.sleep(300)

                except Exception as e:
                    send_alert(f"❌ Error: {e}")
                    print("Error:", e, flush=True)
                    time.sleep(120)

    except Exception as e:
        send_alert(f"❌ Crash: {e}")
        print("Crash:", e, flush=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    run_web()
