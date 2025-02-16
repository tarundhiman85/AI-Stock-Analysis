import requests
import os

def analyze_stock_chart(chart_url):
    """Send the chart to DeepSeek AI for analysis."""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    deepseek_url = f"https://api.deepseek.com/analyze"

    payload = {"chart_url": chart_url}
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.post(deepseek_url, json=payload, headers=headers)
    if response.status_code == 200:
        insights = response.json().get("insights", "No insights available.")
        return insights
    else:
        return "Error analyzing chart."
