from flask import Flask, request, jsonify
import os
from services.telegram_bot import TelegramBotHandler

app = Flask(__name__)

# Load environment variables
app.config['TELEGRAM_BOT_TOKEN'] = os.getenv('TELEGRAM_BOT_TOKEN')

# Set up the Telegram bot
telegram_bot = TelegramBotHandler(app.config['TELEGRAM_BOT_TOKEN'])


@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Telegram webhook endpoint to handle incoming messages."""
    update = request.get_json()
    telegram_bot.process_update(update)
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
