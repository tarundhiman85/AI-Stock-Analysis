import requests

async def analyze_stock_chart_with_ocr(chart_url, api_key):
    """
    Analyzes a stock chart image using OCR.space API and prepares text for analysis.
    
    Args:
        chart_url (str): URL of the stock chart image
        api_key (str): OCR.space API key
        
    Returns:
        str: Analysis prompt containing OCR results
    """
    try:
        # OCR.space API endpoint
        ocr_url = "https://api.ocr.space/parse/imageurl"
        
        # Request parameters
        params = {
            'apikey': api_key,
            'url': chart_url,
            'language': 'eng',
            'isOverlayRequired': False,
            'filetype': 'PNG',
            'detectOrientation': True,
            'OCREngine': 2,  
            'scale': True,
        }
        
        # Make API request
        response = requests.get(ocr_url, params=params)
        
        if response.status_code != 200:
            return f"Error: OCR API request failed with status code {response.status_code}"
            
        result = response.json()
        
        if result.get("OCRExitCode") != 1:
            return f"Error: OCR processing failed with exit code {result.get('OCRExitCode')}"
            
        # Extract parsed text
        texts = ["Stock Chart Analysis Results:"]
        texts.append("\nText detected in chart:")
        
        for page_result in result.get("ParsedResults", []):
            extracted_text = page_result.get("ParsedText", "").strip()
            if extracted_text:
                # Split text into lines and add them as separate entries
                for line in extracted_text.split('\n'):
                    if line.strip():
                        texts.append(f"- {line.strip()}")

        # Combine all detected information
        combined_text = "\n".join(texts)

        # Create analysis prompt
        analysis_prompt = f"""
        Based on the following elements detected in the stock chart:

        {combined_text}

        Please analyze:
        1. Current price trend and momentum
        2. Key support and resistance levels
        3. Notable patterns or formations
        4. Trading volume analysis if visible
        5. Overall market sentiment based on indicators
        6. Potential trading opportunities and risks
        """

        return analysis_prompt

    except Exception as e:
        print(f"OCR Error: {str(e)}")
        return f"Error analyzing image: {str(e)}"