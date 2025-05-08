# FinWiseAI: AI-Powered Personal Finance Advisor with Market Sentiment Analysis

## Overview
FinWiseAI is an AI-powered web application that provides personalized financial advice, investment recommendations, and market sentiment analysis based on user input. The backend leverages generative AI models (`flan-t5-large` for advice generation, `distilbert` for sentiment analysis) and integrates with the Alpha Vantage API for real financial data. The frontend, built with React, displays the results with interactive visualizations (budget pie chart and sentiment bar chart) using Chart.js.

## Features
- **Personalized Financial Advice**: Provides budgeting and investment advice based on user inputs like income, expenses, financial goals, and risk tolerance.
- **Investment Recommendations**: Recommends investment options using real stock data from Alpha Vantage (or mock data if API limits are reached), ranked by relevance and risk alignment.
- **Market Sentiment Analysis**: Analyzes news sentiment using real data from Alpha Vantage (or mock data) and mock social media sentiment (tweets).
- **Interactive Visualizations**: Displays a budget pie chart (Expenses vs. Disposable Income) and a sentiment bar chart (News Sentiment vs. Social Sentiment).

## Tech Stack
- **Backend**:
  - FastAPI (Python)
  - Transformers (`flan-t5-large`, `distilbert`)
  - Sentence-Transformers
  - LangChain
  - FAISS (for vector search)
  - Alpha Vantage API (for stock data and news)
- **Frontend**:
  - React
  - Chart.js (for visualizations)

## Prerequisites
Before running the project, ensure you have the following installed on your device:
- **Python 3.9** or later
- **Node.js** (version 16 or later) and **npm**
- **Git** (to clone the repository)
- An **Alpha Vantage API Key** (free tier available at [Alpha Vantage](https://www.alphavantage.co/))
  - Note: The free tier has a limit of 25 API calls per day. If you exceed this limit, the backend will use mock data.

## Setup Instructions

### 1. Clone the Repository
Clone the project repository from GitHub to your local machine:

```bash
git clone <your-github-repo-url>
cd FinanceAdvisor
```

### 2. Set Up the Backend
The backend is built with FastAPI and requires Python dependencies.

#### a. Navigate to the Project Root
```bash
cd C:\path\to\FinanceAdvisor
```

#### b. Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### c. Install Backend Dependencies
Install the required Python packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

#### d. Set Up the Alpha Vantage API Key
- Open `app/main.py` in a text editor.
- Replace the `ALPHA_VANTAGE_API_KEY` with your own key:
  ```python
  ALPHA_VANTAGE_API_KEY = "your_alpha_vantage_key"
  ```
- Save the file.

#### e. Run the Backend
Start the FastAPI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
- The backend should now be running at `http://localhost:8000`.
- You can verify it by opening `http://localhost:8000/docs` in your browser, which will display the FastAPI Swagger UI.

### 3. Set Up the Frontend
The frontend is built with React and requires Node.js and npm.

#### a. Navigate to the Frontend Directory
```bash
cd frontend
```

#### b. Install Frontend Dependencies
Install the required Node.js packages:
```bash
npm install
```

#### c. Run the Frontend
Start the React development server:
```bash
npm start
```
- The frontend should now be running at `http://localhost:3000` (or a different port if 3000 is occupied, e.g., `http://localhost:3004`).
- The app should automatically open in your default browser.

### 4. Test the Application
- Ensure the backend is running (`http://localhost:8000`).
- Open the frontend in your browser (`http://localhost:3000` or the port shown in the terminal).
- Fill in the form with your financial details:
  - **Annual Income**: e.g., 90000
  - **Annual Expenses**: e.g., 55000
  - **Financial Goals**: e.g., "Save for a vacation"
  - **Risk Tolerance**: e.g., "Moderate"
  - **Sector for Market Sentiment**: e.g., "tech"
- Click "Get Advice".
- The app should display:
  - Personalized financial advice.
  - Investment recommendations (using real data from Alpha Vantage or mock data if rate limits are exceeded).
  - Market sentiment analysis (news sentiment, mock tweets).
  - Visualizations (budget pie chart and sentiment bar chart).

## Troubleshooting
- **Backend Fails to Start**:
  - Ensure all dependencies are installed (`pip install -r requirements.txt`).
  - Check for port conflicts on 8000. If port 8000 is in use, change the port in `main.py` (e.g., to 8001) and update the frontend API calls in `App.js` accordingly.
- **Frontend Fails to Fetch Data**:
  - Ensure the backend is running and accessible at `http://localhost:8000/docs`.
  - Check for CORS errors in the browser console. The CORS middleware in `main.py` allows requests from `http://localhost:3004`. If the frontend runs on a different port, update the `allow_origins` list in `main.py`.
- **Alpha Vantage Rate Limits**:
  - The free API key has a limit of 25 requests per day. If you exceed this, the backend will use mock data. Wait 24 hours for the limit to reset or obtain a new API key.

## Future Improvements
- Add real-time X (Twitter) API integration for social sentiment analysis.
- Enhance visualizations with more charts (e.g., relevance scores for investment recommendations).
- Implement user authentication and persistent data storage.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For any questions or issues, feel free to open an issue on GitHub or contact the project maintainer at [your-email@example.com].