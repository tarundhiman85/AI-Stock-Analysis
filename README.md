
# Stock AI Microservice MVP

## Overview
This project develops a **Python microservice** that integrates **DeepSeek AI** to analyze stock charts and generate insights. The MVP workflow includes:

1. **Telegram Trigger**: Listens for stock-related messages from users.  
2. **Stock Chart Retrieval**: Uses `chartimage.com` API to fetch stock charts with technical indicators.  
3. **OCR-Based Chart Analysis**: Extracts text from the stock chart using **OCR.space API**.  
4. **AI-Driven Insights**: Enhances extracted data using **DeepSeek AI**.  
5. **Telegram Response**: Sends the AI-generated insights along with the chart back to the user.

---

## Tech Stack
- **Backend**: Python (Flask)
- **AI Processing**: DeepSeek API
- **OCR Processing**: OCR.space API
- **Automation Workflow**: n8n (Optional/Future)
- **Data Retrieval**: chartimage.com API
- **Messaging**: Telegram Bot API
- **Storage (Optional)**: Vector Database (e.g., ChromaDB)

---

## Project Roadmap

### Phase 1: Setup & Environment Configuration
- [x] Set up a private GitHub repository.
- [x] Initialize a Python project with a virtual environment.
- [x] Install necessary dependencies (`Flask`, `requests`, `pydantic`, `python-telegram-bot`, `DeepSeek API SDK`, `python-dotenv`).
- [x] Configure environment variables for API keys.
- [ ] Set up a local vector database (if needed).

### Phase 2: Stock Chart Retrieval
- [x] Implement a function to fetch stock charts from `chartimage.com`.
- [x] Ensure the function handles different stock symbols and timeframes.
- [x] Validate API responses and handle errors.

### Phase 3: OCR-Based Chart Processing
- [x] Integrate **OCR.space API** to extract text from stock charts.
- [x] Process OCR results to generate structured data.
- [ ] Optimize OCR text processing for better accuracy.

### Phase 4: AI-Driven Analysis
- [x] Pass OCR-extracted text to **DeepSeek API** for enhanced insights.
- [x] Structure AI-generated insights in a user-friendly format.
- [ ] Implement additional AI enhancements (sentiment analysis, news correlation).

### Phase 5: Telegram Bot Integration
- [x] Set up a Telegram bot using `python-telegram-bot`.
- [x] Implement a command handler to listen for stock-related messages.
- [x] Ensure smooth interaction between Telegram, AI, and chart retrieval.

### Phase 6: Testing & Deployment
- [ ] Test API endpoints using **Postman** or **cURL**.
- [ ] Conduct performance testing on DeepSeek and OCR integrations.
- [ ] Deploy the microservice on a **VPS / Cloud instance** (AWS, GCP, or DigitalOcean).
- [ ] Set up logging and monitoring for debugging.

---

## How to Run Locally

1. **Clone the repository**
   ```sh
   git clone <repo_url>
   cd stock-ai-mvp
   ```

2. **Create a virtual environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file and add:
   ```ini
   TELEGRAM_BOT_TOKEN=<your_token>
   DEEPSEEK_API_KEY=<your_api_key>
   CHARTIMAGE_API_KEY=<your_api_key>
   ```

5. **Run the microservice**
   ```sh
   python flask run
   ```

## Next Steps
- Improved OCR accuracy for better text extraction
- Implement additional AI enhancements (sentiment analysis, news correlation).
- Expand Telegram bot features (custom commands, user preferences).
- Optimize for scalability and cost efficiency.
```

