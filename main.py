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
EMAIL = os.getenv("DVSA_EMAIL")
PASSWORD = os.getenv("DVSA_PASSWORD")
BOOKING = os.getenv("DVSA_BOOKING_REF")

def send_alert(msg):
    try:
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
    except Exception as e:
        print("Telegram failed:", e, flush=True)

def must(value, name):
    if not value:
        raise ValueError(f"{name} is missing in Render Environment")
    return value

def run_bot():
    try:
        subprocess.run(
            ["python", "-m", "playwright", "install", "chromium"],
            check=True
        )

        email = must(EMAIL, "DVSA_EMAIL")
        password = must(PASSWORD, "DVSA_PASSWORD")
        booking = must(BOOKING, "DVSA_BOOKING_REF")

        send_alert("🚀 DVSA bot started")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )

            page = browser.new_page()

            while True:
                try:
                    print("Checking DVSA...", flush=True)

                    page.goto(
                        "https://driverpracticaltest.dvsa.gov.uk/login",
                        timeout=60000
                    )

                    page.wait_for_load_state("networkidle")

                    page.wait_for_selector(
                        'input[name="drivingLicenceNumber"]',
                        timeout=60000
                    )

                    page.fill('input[name="drivingLicenceNumber"]', booking)
                    page.fill('input[name="applicationReferenceNumber"]', email)
                    page.fill('input[name="bookingReference"]', password)

                    page.click("button[type=submit]")

                    page.wait_for_timeout(5000)

                    content = page.content()

                    if "No tests available" not in content:
                        send_alert("🔥 POSSIBLE SLOT FOUND! Check DVSA now.")
                    else:
                        print("No slots found", flush=True)

                    time.sleep(300)

                except Exception as e:
                    send_alert(f"❌ Error: {e}")
                    print("Error:", e, flush=True)
                    time.sleep(60)

    except Exception as e:
        send_alert(f"❌ Crash: {e}")
        print("Crash:", e, flush=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    run_web()
