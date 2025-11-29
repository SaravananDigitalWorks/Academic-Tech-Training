import requests

TELEGRAM_BOT_TOKEN="8138271289:AAHYRa3Q3fYgAQrTwWepqx-lv4l1x-N6d7Q"

TELEGRAM_CHAT_ID="-4678844497"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()
