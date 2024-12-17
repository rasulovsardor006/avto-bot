import requests

token = "7970437752:AAG2CSGAwk3edoqQHBhyEwSWHBzhRJgiKiY"


def notify_user(message, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    return response