import requests
import os

async def analyze_stock_chart(prompt):
    """Send a text prompt to DeepSeek AI and return the response."""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    deepseek_url = "https://api.deepseek.com/v1/chat/completions"  
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",  
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(deepseek_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    except KeyError:
        return "Error parsing API response"