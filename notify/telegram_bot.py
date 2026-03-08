import requests

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, text):
        payload = {"chat_id": self.chat_id, "text": text}
        headers = {"Content-Type": "application/json"}
        r = requests.post(self.url, json=payload, headers=headers)
        print("Telegram response:", r.text)
        return r.json()
