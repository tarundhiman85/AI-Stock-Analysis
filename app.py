import asyncio
from flask import Flask, request, jsonify
import os
import requests
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

app = Flask(__name__)

# Load Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Initialize Telegram Bot Application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Function to fetch stock chart
def fetch_stock_chart(stock_symbol):
    api_key = os.getenv('CHARTIMAGE_API_KEY')
    chart_url = f"https://api.chart-img.com/v1/tradingview/advanced-chart/storage?symbol=NASDAQ:{stock_symbol}&interval=4h&key={api_key}"
    response = requests.get(chart_url)
    
    if response.status_code == 200:
        return response.json().get("url")
    else:
        return "Error fetching chart."

# Function to handle incoming messages
async def handle_message(update: Update, context: CallbackContext):
    print("update", update)
    if not update.channel_post.text:
        print("Received an update without a message, ignoring...")
        return  # Ignore updates that do not contain a message
    
    chat_id = update.channel_post.chat.id
    print("chat_id", chat_id)
    text = update.channel_post.text
    print("text", text)
    
    # await bot.message.reply_text(chat_id=chat_id, text=f"Fetching chart for {text}...")
    print("textagain", "Fetching chart for ...")
    sendmessage = await bot.send_message(chat_id=chat_id, text=f"Fetching chart for {text}...")
    print("sendmessage", sendmessage)
    # await context.bot.send_message(chat_id=chat_id, text=f"Fetching chart for {text}...")
    chart_url = fetch_stock_chart(text)
    print("chart_url", chart_url)
        
    if chart_url:
        await bot.send_photo(chat_id=chat_id, photo=chart_url)
    else:
        await update.message.reply_text("Failed to fetch the stock chart. Try again later.")

# Add handlers to the application
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("Bot is running...")
    application.run_polling()
