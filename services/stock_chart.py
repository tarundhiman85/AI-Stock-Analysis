import requests
import os

def fetch_stock_chart(stock_symbol):
    """Fetch a stock chart from chartimage.com for the given symbol."""
    api_key = os.getenv('CHARTIMAGE_API_KEY')
    chart_url = f"https://api.chartimage.com/v1/chart?symbol={stock_symbol}&apikey={api_key}"
    
    response = requests.get(chart_url)
    if response.status_code == 200:
        return response.json().get("chart_url")
    else:
        return "Error fetching chart."
