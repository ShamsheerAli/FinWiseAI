from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import UserFinanceProfile
from app.db import save_user_profile
from transformers import pipeline
import requests
import tweepy
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LangChainDocument
from langchain_core.embeddings import Embeddings
import os
import re  # For regex-based cleaning

# Set cache directory explicitly to avoid issues
os.environ["TRANSFORMERS_CACHE"] = "C:\\Users\\shams\\.cache\\huggingface\\hub"
os.environ["HF_HOME"] = "C:\\Users\\shams\\.cache\\huggingface\\hub"

app = FastAPI(title="FinWiseAI")

# Add CORS middleware
print("Adding CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3004"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
print("CORS middleware added successfully.")

# Load models
advice_generator = pipeline("text2text-generation", model="google/flan-t5-large", max_length=500, num_beams=5,
                            no_repeat_ngram_size=3)
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
embedder = SentenceTransformer('all-MiniLM-L6-v2')


# Custom embedding class to adapt SentenceTransformer for LangChain, inheriting from Embeddings
class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=False).tolist()

    def embed_query(self, text):
        return self.model.encode([text], show_progress_bar=False)[0].tolist()


# Create an embedding object compatible with LangChain
embedding_wrapper = SentenceTransformerEmbeddings(embedder)

# API Keys (replace with your keys)
ALPHA_VANTAGE_API_KEY = "XBTZFFSH083ZZCZ9"
X_API_KEY = "your_x_api_key"
X_API_SECRET = "your_x_api_secret"
X_ACCESS_TOKEN = "your_x_access_token"
X_ACCESS_TOKEN_SECRET = "your_x_access_token_secret"

# Set up X API (if you have access)
try:
    auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
    auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
    x_api = tweepy.API(auth)
except Exception as e:
    print(f"X API setup failed: {e}")
    x_api = None


# Load market data for investment recommendations with risk labels
def load_market_data():
    try:
        # Fetch data for multiple symbols (e.g., SPY, BND, VNQ for variety)
        symbols = [
            ("SPY", "Aggressive"),  # S&P 500 ETF (broad market, higher risk)
            ("BND", "Conservative"),  # Bond ETF (low risk)
            ("VNQ", "Moderate")  # Real Estate ETF (moderate risk)
        ]
        documents = []
        for symbol, risk in symbols:
            time_series_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
            print(f"Fetching data for {symbol} from URL: {time_series_url}")
            time_series_response = requests.get(time_series_url)
            time_series_response.raise_for_status()
            time_series_data = time_series_response.json()
            print(f"API response for {symbol}: {time_series_data}")

            # Check for error messages in the response
            if "Information" in time_series_data and "rate limit" in time_series_data["Information"].lower():
                print(f"Rate limit exceeded for {symbol}, returning mock data")
                return [
                    LangChainDocument(
                        page_content="Tech sector ETF (TQQQ) - High risk, high reward, suitable for aggressive investors, 15% growth last year.",
                        metadata={"risk": "Aggressive"}),
                    LangChainDocument(
                        page_content="Bond fund (BND) - Low risk, stable returns, ideal for conservative investors, 3% growth last year.",
                        metadata={"risk": "Conservative"}),
                    LangChainDocument(
                        page_content="Real estate investment trust (REIT) - Moderate risk, good for balanced portfolios, 8% growth last year.",
                        metadata={"risk": "Moderate"})
                ]
            if "Error Message" in time_series_data:
                print(f"Error in API response for {symbol}: {time_series_data['Error Message']}, returning mock data")
                return [
                    LangChainDocument(
                        page_content="Tech sector ETF (TQQQ) - High risk, high reward, suitable for aggressive investors, 15% growth last year.",
                        metadata={"risk": "Aggressive"}),
                    LangChainDocument(
                        page_content="Bond fund (BND) - Low risk, stable returns, ideal for conservative investors, 3% growth last year.",
                        metadata={"risk": "Conservative"}),
                    LangChainDocument(
                        page_content="Real estate investment trust (REIT) - Moderate risk, good for balanced portfolios, 8% growth last year.",
                        metadata={"risk": "Moderate"})
                ]

            daily_data = time_series_data.get("Time Series (Daily)", {})
            print(f"Daily data for {symbol}: {daily_data}")
            if daily_data:
                latest_date, latest_data = list(daily_data.items())[0]  # Get the most recent day
                close_price = float(latest_data['4. close'])
                documents.append(
                    LangChainDocument(
                        page_content=f"{symbol} - Close price ${close_price} on {latest_date}, suitable for {risk} investors.",
                        metadata={"risk": risk}
                    )
                )
            else:
                print(f"No daily data available for {symbol}")
        if not documents:
            print("No documents fetched from API, returning mock data")
            return [
                LangChainDocument(
                    page_content="Tech sector ETF (TQQQ) - High risk, high reward, suitable for aggressive investors, 15% growth last year.",
                    metadata={"risk": "Aggressive"}),
                LangChainDocument(
                    page_content="Bond fund (BND) - Low risk, stable returns, ideal for conservative investors, 3% growth last year.",
                    metadata={"risk": "Conservative"}),
                LangChainDocument(
                    page_content="Real estate investment trust (REIT) - Moderate risk, good for balanced portfolios, 8% growth last year.",
                    metadata={"risk": "Moderate"})
            ]
        return documents
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return [
            LangChainDocument(
                page_content="Tech sector ETF (TQQQ) - High risk, high reward, suitable for aggressive investors, 15% growth last year.",
                metadata={"risk": "Aggressive"}),
            LangChainDocument(
                page_content="Bond fund (BND) - Low risk, stable returns, ideal for conservative investors, 3% growth last year.",
                metadata={"risk": "Conservative"}),
            LangChainDocument(
                page_content="Real estate investment trust (REIT) - Moderate risk, good for balanced portfolios, 8% growth last year.",
                metadata={"risk": "Moderate"})
        ]


# Initialize FAISS vector store with market data using the embedding wrapper
try:
    market_documents = load_market_data()
    if not market_documents:
        raise ValueError("Market documents list is empty")
    print("Market documents:", [doc.page_content for doc in market_documents])
    market_vectorstore = FAISS.from_documents(market_documents, embedding_wrapper)
    print("FAISS vector store initialized successfully")
except Exception as e:
    print(f"Error initializing FAISS vector store: {e}")
    raise


@app.post("/financial_advice/")
async def financial_advice(profile: UserFinanceProfile):
    # Save user profile to SQLite
    save_user_profile(profile.income, profile.expenses, profile.goals, profile.risk_tolerance)

    # Calculate disposable income and savings amount
    disposable_income = profile.income - profile.expenses
    savings_percentage = 10
    savings_amount = profile.income * (savings_percentage / 100)

    # Generate financial advice with a simplified prompt and examples
    prompt = (
        "You are a financial advisor. Provide specific budgeting and investment advice based on the user's financial profile:\n"
        "1. Suggest a savings amount as exactly 10% of their income, in the format 'Save $[amount] annually (10% of income).'\n"
        "2. Recommend specific investment options based on their risk tolerance:\n"
        "   - For 'Aggressive', suggest stocks (e.g., individual tech stocks like AAPL).\n"
        "   - For 'Moderate', suggest a mix of balanced ETFs (e.g., VTI) and bonds (e.g., BND) with exact percentage allocations (e.g., 60% VTI, 40% BND).\n"
        "   - For 'Conservative', suggest bonds (e.g., BND) or fixed-income securities with 100% allocation, and explain the choice (e.g., 'for stability').\n"
        "Here are examples:\n"
        "Example 1: Save $6,000 annually (10% of income). Invest 50% in a balanced ETF (e.g., VTI) and 50% in bonds (e.g., BND).\n"
        "Example 2: Save $5,000 annually (10% of income). Invest 60% in a balanced ETF (e.g., VTI) and 40% in bonds (e.g., BND).\n"
        "Example 3: Save $8,000 annually (10% of income). Invest 100% in a bond fund (e.g., BND) for stability.\n"
        "Example 4: Save $10,000 annually (10% of income). Invest in stocks (e.g., individual tech stocks like AAPL).\n"
        "Example 5: Save $9,000 annually (10% of income). Invest 60% in a balanced ETF (e.g., VTI) and 40% in bonds (e.g., BND).\n"
        f"Now, advise the user: A user has an annual income of ${profile.income}, annual expenses of ${profile.expenses}, "
        f"disposable income of ${disposable_income}, goal '{profile.goals}', and {profile.risk_tolerance} risk tolerance."
    )
    advice = advice_generator(prompt, num_return_sequences=1)[0]['generated_text']

    # Post-process the advice to ensure all parts are included
    # Step 1: Replace $[amount] with the calculated savings amount
    advice = advice.replace("$[amount]", f"${savings_amount:,.0f}")

    # Step 2: Remove any "Example [number]:" phrases
    advice = re.sub(r'Example \d+:', '', advice).strip()

    # Step 3: Remove any prompt-like instructions (e.g., "For '[risk_tolerance]'")
    advice = re.sub(r"For '[A-Za-z]+', suggest [^\.]+?\.", '', advice).strip()

    # Step 4: Prepend the user profile summary
    profile_summary = (
        f"A user has an annual income of ${profile.income:,.0f}, annual expenses of ${profile.expenses:,.0f}, "
        f"disposable income of ${disposable_income:,.0f}, goal \"{profile.goals}\", and {profile.risk_tolerance} risk tolerance. "
    )
    advice = profile_summary + advice

    # Step 5: Remove any existing "Additionally," sentence and append the correct tips
    advice = advice.split("Additionally,")[0].strip()  # Remove any existing tips
    if profile.risk_tolerance == "Conservative":
        advice += " Additionally, consult a financial planner, and automate savings."
    elif profile.risk_tolerance == "Aggressive":
        advice += " Additionally, diversify your investments, and monitor market trends."
    else:  # Moderate
        advice += f" Additionally, build an emergency fund of ${disposable_income / 2:,.0f}-${disposable_income:,.0f}, and review your portfolio annually."

    return {"advice": advice}


@app.get("/market_sentiment/{sector}")
async def market_sentiment(sector: str):
    news_texts = []
    if ALPHA_VANTAGE_API_KEY != "your_alpha_vantage_key":
        try:
            news_url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics={sector}&apikey={ALPHA_VANTAGE_API_KEY}"
            news_response = requests.get(news_url)
            news_response.raise_for_status()
            news_data = news_response.json()
            if "feed" not in news_data:
                raise HTTPException(status_code=500, detail="No news data available from Alpha Vantage")
            news_articles = news_data.get("feed", [])[:5]
            news_texts = [article.get("summary", "") for article in news_articles if "summary" in article]
        except Exception as e:
            print(f"Error fetching news: {e}")
            news_texts = []
    else:
        print("Alpha Vantage API key not set. Using empty news data.")

    tweet_texts = []
    if x_api:
        try:
            tweets = x_api.search_tweets(q=f"{sector} finance", count=50, lang="en")
            tweet_texts = [tweet.text for tweet in tweets if tweet.text]
        except Exception as e:
            print(f"Error fetching tweets: {e}")
            tweet_texts = [
                f"The {sector} sector is booming right now! #invest",
                f"Not sure about {sector}, seems risky. #finance"
            ]
    else:
        print("X API not set up. Using mock data for tweets.")
        tweet_texts = [
            f"The {sector} sector is booming right now! #invest",
            f"Not sure about {sector}, seems risky. #finance"
        ]

    news_sentiments = [sentiment_analyzer(text)[0]['label'] for text in news_texts if text]
    news_sentiment = "POSITIVE" if news_sentiments.count("POSITIVE") > len(
        news_sentiments) / 2 else "NEGATIVE" if news_sentiments else "NEUTRAL"

    tweet_sentiments = [sentiment_analyzer(text)[0]['label'] for text in tweet_texts if text]
    avg_tweet_sentiment = "POSITIVE" if tweet_sentiments.count("POSITIVE") > len(
        tweet_sentiments) / 2 else "NEGATIVE" if tweet_sentiments else "NEUTRAL"

    return {
        "news_sentiment": news_sentiment,
        "social_sentiment": avg_tweet_sentiment,
        "news_articles": news_texts,
        "tweets": tweet_texts
    }


@app.post("/investment_recommendations/")
async def investment_recommendations(profile: UserFinanceProfile):
    try:
        # Create a query based on user preferences
        query = f"Investment opportunities for a user with goals: {profile.goals}, risk tolerance: {profile.risk_tolerance}"
        print(f"Query: {query}")

        # Search for similar market opportunities with scores
        results = market_vectorstore.similarity_search_with_score(query, k=3)  # Include all 3 documents
        print(f"Search results: {[(doc.page_content, score) for doc, score in results]}")

        # Adjust relevance scores based on risk tolerance alignment
        risk_mapping = {
            "Conservative": {"Conservative": 1.0, "Moderate": 0.5, "Aggressive": 0.0},
            "Moderate": {"Conservative": 0.4, "Moderate": 1.0, "Aggressive": 0.6},
            # Favor Aggressive slightly over Conservative
            "Aggressive": {"Conservative": 0.0, "Moderate": 0.5, "Aggressive": 2.0}
        }
        adjusted_results = []
        for doc, distance in results:
            # Lower distance = higher similarity in FAISS
            similarity = 1.0 / (1.0 + distance)  # Convert distance to similarity (0 to 1)
            # Adjust similarity based on risk alignment
            doc_risk = doc.metadata.get("risk", "Moderate")  # Default to Moderate if not specified
            risk_adjustment = risk_mapping.get(profile.risk_tolerance, {}).get(doc_risk, 0.5)
            adjusted_score = similarity * risk_adjustment
            adjusted_results.append((doc, adjusted_score))

        # Sort by adjusted score (descending)
        adjusted_results.sort(key=lambda x: x[1], reverse=True)

        # Take top 2 results
        adjusted_results = adjusted_results[:2]

        # Normalize adjusted scores to 0-1 range
        max_score = max(score for _, score in adjusted_results) if adjusted_results else 1.0
        min_score = min(score for _, score in adjusted_results) if adjusted_results else 0.0
        if max_score == min_score:
            max_score += 1e-6  # Avoid division by zero
        recommendations = [
            {
                "description": doc.page_content,
                "relevance_score": float((score - min_score) / (max_score - min_score))
            }
            for doc, score in adjusted_results
        ]
        return {"recommendations": recommendations}
    except Exception as e:
        print(f"Error in investment_recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)