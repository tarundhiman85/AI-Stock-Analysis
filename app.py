import asyncio
from flask import Flask, request, jsonify
import os
import requests
from services.ai_analysis import analyze_stock_chart_async
from services.cloud_vision import analyze_stock_chart_with_ocr
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import http.client, urllib.parse
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import chromadb


# Initialize ChromaDB client
client = chromadb.Client()
try:
    collection = client.create_collection("articles")
except ValueError:
    # Collection might already exist
    collection = client.get_collection("articles")


load_dotenv()

app = Flask(__name__)

# Load Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OCR_TOKEN = os.getenv('OCR_TOKEN')
bot = Bot(token=TELEGRAM_BOT_TOKEN)
analyzer = SentimentIntensityAnalyzer()

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
        return None


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
        try:
            response_json = json.loads(data.decode('utf-8'))
            news_list = [{"title": article["title"], "url": article["url"], "summary": article.get("summary", "No summary available")} for article in response_json.get("data", [])]
            
            # Process and store each news article with sentiment classification
            for news in news_list:
                sentiment = classify_sentiment(news["summary"])
                # Store article summary and sentiment in ChromaDB
                try:
                    collection.add(
                        documents=[news["summary"]],
                        metadatas=[{"title": news["title"], "url": news["url"], "sentiment": sentiment}],
                        ids=[str(hash(news["title"]))]  # Use hash of title as ID to avoid collisions
                    )
                except Exception as e:
                    print(f"Error storing article in ChromaDB: {e}")
            
            return news_list
        except Exception as e:
            print(f"Error processing news data: {e}")
            return []
    else:
        return []


# Function to classify sentiment
def classify_sentiment(text: str) -> str:
    if not text or text == "No summary available":
        return 'neutral'
    
    sentiment_score = analyzer.polarity_scores(text)
    compound_score = sentiment_score['compound']
    
    if compound_score >= 0.05:
        return 'positive'
    elif compound_score <= -0.05:
        return 'negative'
    else:
        return 'neutral'
    
# Fixed function to handle incoming messages
async def handle_message(update: Update, context: CallbackContext):
    try:
        message = update.message if update.message else update.channel_post
        if not message:
            return
            
        chat_id = message.chat.id
        text = message.text
        
        if not text:
            await bot.send_message(chat_id=chat_id, text="Please send a valid stock symbol.")
            return
            
        # Clean and prepare the stock symbol
        stock_symbol = text.strip().upper()
        
        await bot.send_message(chat_id=chat_id, text=f"Fetching chart for {stock_symbol}...")

        chart_url = fetch_stock_chart(stock_symbol)

        if chart_url:
            try:
                # Get OCR analysis of the chart
                analysis_prompt = await analyze_stock_chart_with_ocr(chart_url, OCR_TOKEN)
                
                # Use the async version of analyze_stock_chart with timeout handling
                try:
                    analysis_result = await asyncio.wait_for(
                        analyze_stock_chart_async(stock_symbol, analysis_prompt or ""), 
                        timeout=120
                    )
                    
                    # If analysis_result is None or empty, provide a default message
                    if not analysis_result:
                        analysis_result = f"Unable to analyze {stock_symbol} at this time. Please try again later."
                        
                    # Send the chart image
                    await bot.send_photo(chat_id=chat_id, photo=chart_url)
                    
                    # Send analysis result
                    await bot.send_message(chat_id, text=analysis_result)
                except asyncio.TimeoutError:
                    await bot.send_message(
                        chat_id, 
                        text=f"Analysis for {stock_symbol} is taking too long. Here's the chart:",
                    )
                    await bot.send_photo(chat_id=chat_id, photo=chart_url)
            except Exception as e:
                print(f"Error during chart analysis: {e}")
                await bot.send_message(
                    chat_id, 
                    text=f"Error analyzing chart for {stock_symbol}. Here's the chart anyway:",
                )
                await bot.send_photo(chat_id=chat_id, photo=chart_url)
            
            # Fetch and send news along with sentiment
            try:
                await bot.send_message(chat_id, text=f"Fetching news articles related to {stock_symbol}...")
                news_source = await fetch_news_source(stock_symbol)
                
                if news_source and len(news_source) > 0:
                    for news in news_source:
                        sentiment = classify_sentiment(news["summary"])
                        emoji = "✅" if sentiment == "positive" else "❌" if sentiment == "negative" else "⚠️"
                        news_message = f"{emoji} *{news['title']}*\n🔗 [Read More]({news['url']})\nSentiment: {sentiment.capitalize()}"
                        await bot.send_message(chat_id, text=news_message, parse_mode="Markdown")
                else:
                    await bot.send_message(chat_id, text=f"No recent news found for {stock_symbol}.")
            except Exception as e:
                print(f"Error fetching news: {e}")
                await bot.send_message(chat_id, text="Failed to fetch news. Try again later.")
        else:
            await bot.send_message(chat_id=chat_id, text=f"Failed to fetch the chart for {stock_symbol}. Please verify the symbol and try again.")
    except Exception as e:
        print(f"Unhandled error in handle_message: {e}")
        try:
            await bot.send_message(update.message.chat.id, text="An error occurred while processing your request. Please try again.")
        except:
            pass  # If we can't even send this message, there's not much else we can do

# Add handlers to the application
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("Bot is running...")
    application.run_polling()