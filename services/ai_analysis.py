import os
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import Field
import aiohttp
from typing import Any, Optional, List

# Define global API keys for Alpha Vantage and DeepSeek
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY') or ""
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY') or ""

class DeepSeekLLM(LLM):
    """Custom LangChain LLM class for DeepSeek AI."""
    
    api_key: str = Field(..., description="API key for DeepSeek")
    model_name: str = Field(default="deepseek-chat")
    api_url: str = Field(default="https://api.deepseek.com/v1/chat/completions")
    temperature: float = Field(default=0.7, description="Sampling temperature for response diversity")
    
    def __init__(self, api_key=None, **kwargs):
        """Initialize the DeepSeek LLM with API key."""
        api_key = api_key or DEEPSEEK_API_KEY or ""
        if not api_key:
            print("Warning: DeepSeek API key is not set")
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
        """Call the DeepSeek API and return the response (sync version kept for LangChain compatibility)."""
        # This is kept to maintain compatibility with the LangChain LLM base class
        # In practice, we'll be using the async version
        raise NotImplementedError("Please use the async version of this method")
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """Asynchronously call the DeepSeek API and return the response."""
        if not prompt:
            return "No prompt provided for analysis."
            
        if not self.api_key:
            return "API key not configured. Please set the DEEPSEEK_API_KEY environment variable."
            
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
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"DeepSeek API error: {response.status} - {error_text}")
                        return "Analysis failed. Please try again later."
                    
                    response_json = await response.json()
                    result = response_json.get('choices', [{}])[0].get('message', {}).get('content')
                    return result if result else "No analysis results obtained."
        except Exception as e:
            print(f"DeepSeek API error: {str(e)}")
            return "Analysis failed. Please try again later."
    
    @property
    def _identifying_params(self) -> dict:
        """Get identifying parameters for the LLM."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature
        }

# Asynchronous fetch historical data function
async def async_fetch_historical_data(stock_symbol, output_size="compact"):
    """
    Asynchronously fetch historical stock data (price and volume) from Alpha Vantage API.
    
    :param stock_symbol: Stock symbol (e.g., 'AAPL')
    :param output_size: 'compact' (last 100 data points) or 'full' (full-length data)
    :return: List of dates with price and volume data, or empty list if there's an error.
    """
    if not stock_symbol:
        print("No stock symbol provided")
        return []
        
    if not ALPHA_VANTAGE_API_KEY:
        print("Alpha Vantage API key not set")
        return []
        
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock_symbol,
        "apikey": ALPHA_VANTAGE_API_KEY, 
        "outputsize": output_size  
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    try:
                        # Parse the data into a list of tuples (date, close price, volume)
                        time_series = data.get("Time Series (Daily)", {})
                        if not time_series:
                            print(f"No time series data found for {stock_symbol}")
                            return []
                            
                        historical_data = []
                        
                        for date, values in time_series.items():
                            try:
                                close_price = float(values.get("4. close", 0))
                                volume = int(values.get("5. volume", 0))
                                historical_data.append((date, close_price, volume))
                            except (ValueError, TypeError) as e:
                                print(f"Error parsing data for date {date}: {e}")
                        
                        return historical_data
                    except KeyError as e:
                        print(f"Error in parsing data: {e}")
                        return []
                else:
                    error_text = await response.text()
                    print(f"Error fetching data from Alpha Vantage: {response.status} - {error_text}")
                    return []
    except Exception as e:
        print(f"Exception when fetching historical data: {e}")
        return []

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
    try:
        oldest_date = sorted_data[-1][0]
        newest_date = sorted_data[0][0]
        price_change = sorted_data[0][1] - sorted_data[-1][1]
        price_change_pct = (price_change / sorted_data[-1][1]) * 100 if sorted_data[-1][1] != 0 else 0
        
        avg_volume = sum(volume for _, _, volume in sorted_data) / len(sorted_data) if sorted_data else 0
        max_volume = max(volume for _, _, volume in sorted_data) if sorted_data else 0
        min_volume = min(volume for _, _, volume in sorted_data) if sorted_data else 0
        
        summary = f"\nSummary Statistics:\n"
        summary += f"- Date Range: {oldest_date} to {newest_date}\n"
        summary += f"- Price Change: ${price_change:.2f} ({price_change_pct:.2f}%)\n"
        summary += f"- Average Volume: {avg_volume:,.0f}\n"
        summary += f"- Volume Range: {min_volume:,} to {max_volume:,}\n"
        
        return formatted + summary
    except Exception as e:
        print(f"Error generating summary statistics: {e}")
        return formatted + "\nUnable to generate summary statistics."

# Create asynchronous stock analysis chain
def create_async_stock_analysis_chain():
    """
    Create an asynchronous LangChain for stock chart analysis with DeepSeek API,
    enhanced with historical data from Alpha Vantage.
    
    :return: A runnable chain for stock analysis
    """
    # Initialize LLM with DeepSeek API key
    llm = DeepSeekLLM(api_key=DEEPSEEK_API_KEY)
    
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
        template=template
    )
    
    async def async_chain_func(inputs: dict) -> str:
        stock_symbol = inputs.get("stock_symbol") or ""
        additional_context = inputs.get("additional_context") or ""
        
        if not stock_symbol:
            return "Error: No stock symbol provided."
        
        # If historical_data is provided, use it; otherwise fetch it
        historical_data = inputs.get("historical_data")
        
        if not historical_data:
            # Fetch historical data from Alpha Vantage
            historical_data = await async_fetch_historical_data(stock_symbol)
            
            if not historical_data:
                return f"Error: Unable to fetch historical data for {stock_symbol}. Please check if the symbol is correct and try again."
        
        # Format the historical data for the prompt
        formatted_data = format_historical_data(historical_data) if historical_data else "No historical data provided."
        
        # Apply the prompt template to the input data
        prompt = prompt_template.format(
            stock_symbol=stock_symbol,
            historical_data=formatted_data,
            additional_context=additional_context
        )
        
        try:
            result = await llm._acall(prompt)
            return result or f"No analysis could be generated for {stock_symbol}."
        except Exception as e:
            print(f"Error in async_chain_func: {e}")
            return f"Error analyzing {stock_symbol}. Please try again later."
    
    return RunnableLambda(async_chain_func)

# Asynchronous function for stock analysis
async def analyze_stock_chart_async(stock_symbol, additional_context=""):
    """
    Asynchronously analyze stock chart data using LangChain with historical data.
    
    :param stock_symbol: The stock symbol to analyze (e.g., 'AAPL')
    :param additional_context: Additional context or questions for the analysis
    :return: Analysis results
    """
    if not stock_symbol:
        return "Error: No stock symbol provided."
        
    additional_context = additional_context or ""
    
    try:
        # Create the async analysis chain
        analysis_chain = create_async_stock_analysis_chain()
        
        # Use ainvoke() for asynchronous execution
        result = await analysis_chain.ainvoke({
            "stock_symbol": stock_symbol,
            "additional_context": additional_context
        })
        
        return result or f"No analysis could be generated for {stock_symbol}."
    except Exception as e:
        print(f"LangChain Error: {str(e)}")
        return f"Error analyzing {stock_symbol}. Please try again later."