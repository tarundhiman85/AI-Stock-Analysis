import requests
from services.stock_chart import fetch_stock_chart
from services.ai_analysis import analyze_stock_chart

class TelegramBotHandler:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, chat_id, text):
        """Send a message to the user."""
        url = f"{self.api_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        requests.post(url, json=payload)

    def process_update(self, update):
        """Process incoming messages."""
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"].get("text", "").strip()

            if text.startswith("/stock"):
                stock_symbol = text.split(" ")[1]
                chart_url = fetch_stock_chart(stock_symbol)
                analysis = analyze_stock_chart(chart_url)
                response_message = f"Chart Analysis for {stock_symbol}:\n\n{analysis}"
                self.send_message(chat_id, response_message)
