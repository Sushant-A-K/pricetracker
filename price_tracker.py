import smtplib
import time
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
ALERT_TO  = os.getenv("ALERT_TO")


PRODUCTS = [
    {
        "name": "Green Soul Table Height Adjustable",
        "url": "https://www.amazon.in/dp/B0D66XCLCS",
        "threshold": 18000
    },
    {
        "name": "Logitech G29",
        "url": "https://www.amazon.in/dp/B013DYX7BS",
        "threshold": 30000
    },
    {
        "name": "Green Soul Table Height Adjustable RGB Wireless",
        "url": "https://www.amazon.in/dp/B0FPFRP1BP",
        "threshold": 40000
    }
]

# ---------- Core Functions ----------


def get_price(driver, url):
    driver.get(url)
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    price_span = soup.select_one("span.a-price-whole")
    if not price_span:
        raise ValueError("Price not found")

    raw = price_span.text.strip()

    # Keep only digits
    cleaned = re.sub(r"[^\d]", "", raw)

    if not cleaned:
        raise ValueError(f"Could not clean price from: {raw}")

    return int(cleaned)


def send_email(product, price):
    msg = MIMEText(
        f"{product['name']} dropped to ₹{price}\n\n{product['url']}"
    )
    msg["Subject"] = f"💰 Price Drop: {product['name']}"
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f"📧 Alert sent for {product['name']}")

# ---------- Main ----------

def main():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for product in PRODUCTS:
        try:
            price = get_price(driver, product["url"])
            print(f"{product['name']} → ₹{price}")

            if price <= product["threshold"]:
                send_email(product, price)
            else:
                print("   No alert.")

        except Exception as e:
            print(f"❌ Failed for {product['name']}: {e}")

        time.sleep(15)  # delay between products (anti-ban)

    driver.quit()

if __name__ == "__main__":
    main()
