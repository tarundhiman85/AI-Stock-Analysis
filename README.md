# Stock AI Microservice MVP

## Overview
This project aims to develop a Python microservice that integrates DeepSeek AI to analyze stock charts and generate insights. The MVP will work as follows:

- **Telegram Trigger:** Listens for stock-related messages from users.
- **Stock Chart Retrieval:** Uses chartimage.com API to fetch stock charts with technical indicators.
- **Basic Analysis:** Extracts key insights from the chart.
- **Detailed Analysis:** Enhances the insights using DeepSeek AI.
- **Telegram Response:** Sends the analysis along with the chart back to the user.

## Tech Stack
- **Backend:** Python (FastAPI / Flask)
- **AI Processing:** DeepSeek API
- **Automation Workflow:** n8n (Optional/Future)
- **Data Retrieval:** chartimage.com API
- **Messaging:** Telegram Bot API
- **Storage (Optional):** Vector Database (e.g., ChromaDB)

## Project Roadmap

**Phase 1: Setup & Environment Configuration**
- [ ] Set up a private GitHub repository.
- [ ] Initialize a Python project with a virtual environment.
- [ ] Install necessary dependencies (FastAPI, requests, pydantic, python-telegram-bot, DeepSeek API SDK).
- [ ] Configure environment variables for API keys.
- [ ] Set up a local vector database (if needed).

**Phase 2: Stock Chart Retrieval**
- [ ] Implement a function to fetch stock charts from chartimage.com.
- [ ] Ensure the function can handle different stock symbols and timeframes.
- [ ] Validate API responses and handle errors.

**Phase 3: AI Analysis**
- [ ] Integrate DeepSeek API for basic analysis.
- [ ] Process stock charts and generate initial insights.
- [ ] Store and retrieve data using a vector database (if required).

**Phase 4: Enhanced Analysis with AI**
- [ ] Pass the initial insights to DeepSeek API for a more refined analysis.
- [ ] Structure responses in a user-friendly format.

**Phase 5: Telegram Bot Integration**
- [ ] Set up a Telegram bot using python-telegram-bot.
- [ ] Implement a command handler to listen for stock-related messages.
- [ ] Ensure smooth interaction between Telegram, AI, and chart retrieval.

**Phase 6: Testing & Deployment**
- [ ] Test API endpoints using Postman or cURL.
- [ ] Conduct performance testing on DeepSeek integration.
- [ ] Deploy the microservice on a VPS / Cloud instance (e.g., AWS, GCP, or DigitalOcean).
- [ ] Set up logging and monitoring for debugging.

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
   uvicorn app:main --reload  # For FastAPI
   ```

## Next Steps
- Implement additional AI enhancements (sentiment analysis, news correlation).
- Expand Telegram bot features (custom commands, user preferences).
- Optimize for scalability and cost efficiency.
```

