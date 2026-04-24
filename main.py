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
DVSA_EMAIL = os.getenv("DVSA_EMAIL")
DVSA_PASSWORD = os.getenv("DVSA_PASSWORD")

CENTRES = ["Bromley", "Gillingham", "Sevenoaks", "Birmingham", "London", "Croydon"]

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

        send_alert("✅ DVSA checker started")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            send_alert("Opening DVSA login page")
            page.goto("https://driverpracticaltest.dvsa.gov.uk/login", timeout=60000)

            send_alert("DVSA page opened")

            while True:
                try:
                    page_text = page.inner_text("body")

                    found = []
                    for centre in CENTRES:
                        if centre.lower() in page_text.lower():
                            found.append(centre)

                    if found:
                        send_alert(
                            "🚨 Possible DVSA centre found:\n\n"
                            + "\n".join(found)
                            + "\n\nCheck now:\nhttps://driverpracticaltest.dvsa.gov.uk/login"
                        )

                    print("Checked DVSA page", flush=True)
                    time.sleep(180)

                except Exception as e:
                    send_alert(f"❌ Check error: {e}")
                    time.sleep(180)

    except Exception as e:
        send_alert(f"❌ Bot error: {e}")
        print("Error:", e, flush=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    run_web()
