import os
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import Field
import requests
from typing import Any, Optional, List

# Define global API keys for Alpha Vantage and DeepSeek
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY') 
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

class DeepSeekLLM(LLM):
    """Custom LangChain LLM class for DeepSeek AI."""
    
    api_key: str = Field(..., description="API key for DeepSeek")
    model_name: str = Field(default="deepseek-chat")
    api_url: str = Field(default="https://api.deepseek.com/v1/chat/completions")
    temperature: float = Field(default=0.7, description="Sampling temperature for response diversity")
    
    def __init__(self, api_key=None, **kwargs):
        """Initialize the DeepSeek LLM with API key."""
        api_key = api_key or DEEPSEEK_API_KEY  
        super().__init__(api_key=api_key, **kwargs)
        
    @property
    def _llm_type(self) -> str:
        return "deepseek"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """Call the DeepSeek API and return the response."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        if stop:
            payload["stop"] = stop
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"DeepSeek API error: {str(e)}, falling back to original implementation")
            return fallback_analyze_stock_chart(prompt)
        except KeyError as e:
            print(f"DeepSeek API response parsing error: {str(e)}, falling back to original implementation")
            return fallback_analyze_stock_chart(prompt)
    
    @property
    def _identifying_params(self) -> dict:
        """Get identifying parameters for the LLM."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature
        }

# Fallback function
def fallback_analyze_stock_chart(prompt):
    """Fallback stock analysis function."""
    deepseek_url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",  
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(deepseek_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    except KeyError:
        return "Error parsing API response"

def fetch_historical_data(stock_symbol, output_size="compact"):
    """
    Fetch historical stock data (price and volume) from Alpha Vantage API.
    
    :param stock_symbol: Stock symbol (e.g., 'AAPL')
    :param output_size: 'compact' (last 100 data points) or 'full' (full-length data)
    :return: List of dates with price and volume data, or None if there's an error.
    """
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock_symbol,
        "apikey": ALPHA_VANTAGE_API_KEY, 
        "outputsize": output_size  
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        try:
            # Parse the data into a list of tuples (date, close price, volume)
            time_series = data.get("Time Series (Daily)", {})
            historical_data = []
            
            for date, values in time_series.items():
                close_price = float(values["4. close"])
                volume = int(values["5. volume"])
                historical_data.append((date, close_price, volume))
            
            return historical_data
        except KeyError:
            print(f"Error in parsing data: {data}")
            return None
    else:
        print(f"Error fetching data from Alpha Vantage: {response.status_code}")
        return None

# Create the enhanced stock analysis chain with historical data
def create_stock_analysis_chain():
    """
    Create a LangChain for stock chart analysis with DeepSeek API,
    enhanced with historical data from Alpha Vantage.
    
    :return: A runnable chain for stock analysis
    """
    # Initialize LLM with DeepSeek API key
    llm = DeepSeekLLM(api_key=DEEPSEEK_API_KEY)  # Use the global DEEPSEEK_API_KEY
    
    # Define the prompt template with enhanced historical data
    template = """
    You are an expert financial analyst specialized in technical analysis of stock charts.
    
    Analyze the following historical stock data for {stock_symbol}. The data includes date, closing price, and trading volume.
    
    Historical Data:
    {historical_data}
    
    Perform a comprehensive analysis including:
    
    1. Correlation Analysis:
       - Calculate the correlation coefficient between stock price and trading volume
       - Explain what this correlation means (value between -1 and 1, where -1 is strong negative correlation, 1 is strong positive correlation, and 0 is no correlation)
       - Identify any periods where correlation patterns changed
    
    2. Price Trend Analysis:
       - Identify key support and resistance levels
       - Note any significant price patterns (e.g., head and shoulders, double tops/bottoms)
       - Calculate and interpret moving averages (if applicable)
    
    3. Volume Analysis:
       - Identify unusual volume spikes and their relationship to price movements
       - Assess volume trends compared to price movements
    
    4. Market Insights:
       - Provide contextual interpretation of the data patterns
       - Identify potential anomalies or outliers in the data
    
    5. Trading Strategy Recommendations:
       - Suggest potential entry and exit points based on the analysis
       - Recommend appropriate risk management strategies
    
    Additional Context:
    {additional_context}
    
    Your analysis should be data-driven, objective, and based on the technical aspects.
    Note: Response should be strictly within 4000 characters and also respone should be in MARKDOWN format so that text can be sent in formatted way. 
    """
    
    prompt_template = PromptTemplate(
        input_variables=["stock_symbol", "historical_data", "additional_context"],
        template=template,
    )
    
    def format_historical_data(data):
        """Format historical data into a readable table format."""
        if not data:
            return "No historical data available."
        
        # Sort data by date (newest first)
        sorted_data = sorted(data, key=lambda x: x[0], reverse=True)
        
        # Create a formatted table with headers
        formatted = "Date | Close Price | Volume\n"
        formatted += "-----|------------|--------\n"
        
        # Add data rows (limit to 30 entries to keep prompt size reasonable)
        for date, price, volume in sorted_data[:30]:
            formatted += f"{date} | ${price:.2f} | {volume:,}\n"
            
        # Add summary statistics
        oldest_date = sorted_data[-1][0]
        newest_date = sorted_data[0][0]
        price_change = sorted_data[0][1] - sorted_data[-1][1]
        price_change_pct = (price_change / sorted_data[-1][1]) * 100
        
        avg_volume = sum(volume for _, _, volume in sorted_data) / len(sorted_data)
        max_volume = max(volume for _, _, volume in sorted_data)
        min_volume = min(volume for _, _, volume in sorted_data)
        
        summary = f"\nSummary Statistics:\n"
        summary += f"- Date Range: {oldest_date} to {newest_date}\n"
        summary += f"- Price Change: ${price_change:.2f} ({price_change_pct:.2f}%)\n"
        summary += f"- Average Volume: {avg_volume:,.0f}\n"
        summary += f"- Volume Range: {min_volume:,} to {max_volume:,}\n"
        
        return formatted + summary
    
    def chain_func(inputs: dict) -> str:
        stock_symbol = inputs.get("stock_symbol")
        additional_context = inputs.get("additional_context", "")
        
        # If historical_data is provided, use it; otherwise fetch it
        historical_data = inputs.get("historical_data")
        
        if not historical_data and stock_symbol:
            # Fetch historical data from Alpha Vantage
            historical_data = fetch_historical_data(stock_symbol)
            
            if not historical_data:
                return "Error: Unable to fetch historical data for the specified stock symbol."
        
        # Format the historical data for the prompt
        formatted_data = format_historical_data(historical_data) if historical_data else "No historical data provided."
        
        # Apply the prompt template to the input data
        prompt = prompt_template.format(
            stock_symbol=stock_symbol,
            historical_data=formatted_data,
            additional_context=additional_context
        )
        
        return llm._call(prompt)
    
    return RunnableLambda(chain_func)

# Stock analysis function - now synchronous
async def analyze_stock_chart(stock_symbol, additional_context=""):
    """
    Analyze stock chart data using LangChain with historical data.
    
    :param stock_symbol: The stock symbol to analyze (e.g., 'AAPL')
    :param additional_context: Additional context or questions for the analysis
    :return: Analysis results
    """
    try:
        # Create the analysis chain
        analysis_chain = create_stock_analysis_chain()
        
        # Use invoke() instead of run()
        result = analysis_chain.invoke({
            "stock_symbol": stock_symbol,
            "additional_context": additional_context
        })
        
        return result
    except Exception as e:
        print(f"LangChain Error: {str(e)}")
        # Create a basic prompt for the fallback method
        prompt = f"""
        Analyze the stock data for {stock_symbol}.
        
        Additional context: {additional_context}
        
        Provide a technical analysis of this stock including price trends and volume analysis.
        """
        # Fall back to the original method
        return fallback_analyze_stock_chart(prompt)