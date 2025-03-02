import asyncio
from flask import Flask, request, jsonify
import os
import requests
from services.ai_analysis import analyze_stock_chart
from services.cloud_vision import analyze_stock_chart_with_ocr
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import http.client, urllib.parse
import json
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Load Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OCR_TOKEN = os.getenv('OCR_TOKEN')
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


async def fetch_news_source(stock_symbol):
    FINANCE_NEWS_API = os.getenv('FINANCE_NEWS_API')
    conn = http.client.HTTPSConnection('api.marketaux.com')
    params = urllib.parse.urlencode({
       'api_token': FINANCE_NEWS_API,
       'symbols': stock_symbol,
       'language': 'en,hi',
       'limit': 3,
    })
    conn.request('GET', '/v1/news/all?{}'.format(params))
    res = conn.getresponse()
    data = res.read()
    if data:
        response_json = json.loads(data.decode('utf-8'))
        print("res json", response_json)
        news_list = [{"title": article["title"], "url": article["url"]} for article in response_json.get("data", [])]
        print("News List:", news_list)
        return news_list
    else:
        return "Error fetching news."


# Function to handle incoming messages
async def handle_message(update: Update, context: CallbackContext):
    print("update", update)
    
    # Check for the existence of a message or channel_post
    message = update.message if update.message else update.channel_post
    
    chat_id = message.chat.id
    text = message.text
    await bot.send_message(chat_id=chat_id, text=f"Fetching chart for {text}...")
    
    chart_url = fetch_stock_chart(text)
    # analysis_prompt = f"Please analyze this stock chart for {text} and provide key insights about price trends, support/resistance levels, and potential trading opportunities."    
    # analysis_result = analyze_stock_chart(chart_url, analysis_prompt)
    if chart_url:
        analysis_prompt = await analyze_stock_chart_with_ocr(chart_url, OCR_TOKEN)
        analysis_result = await analyze_stock_chart(analysis_prompt)
        await bot.send_photo(chat_id=chat_id, photo=chart_url)
        await bot.send_message(chat_id, analysis_result)
        news_source = await fetch_news_source(text)
        if news_source:
            await bot.send_message(chat_id, text=f"Fetching News Article Related to {text}...")
            for news in news_source:
                news_message = f"📢 *Title:* {news['title']}\n🔗 [Read More]({news['url']})"
                await bot.send_message(chat_id, text=news_message, parse_mode="Markdown")
        else:
            await bot.send_message(chat_id, text="No news found for this stock.")
    else:
        await bot.send_message(chat_id=chat_id, text="Failed to fetch the stock chart. Try again later.")

# Add handlers to the application
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("Bot is running...")
    application.run_polling()
