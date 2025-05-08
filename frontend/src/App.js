import React, { useState, useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import './App.css';

function App() {
    const [formData, setFormData] = useState({
        income: '',
        expenses: '',
        goals: '',
        risk_tolerance: '',
        sector: ''
    });
    const [advice, setAdvice] = useState(null);
    const [recommendations, setRecommendations] = useState(null);
    const [sentiment, setSentiment] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Use refs to store chart instances
    const budgetChartRef = useRef(null);
    const sentimentChartRef = useRef(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            console.log("Fetching financial advice...");
            const adviceResponse = await fetch('http://localhost:8000/financial_advice/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    income: parseFloat(formData.income),
                    expenses: parseFloat(formData.expenses),
                    goals: formData.goals,
                    risk_tolerance: formData.risk_tolerance
                })
            });
            if (!adviceResponse.ok) {
                throw new Error(`Financial advice fetch failed: ${adviceResponse.statusText}`);
            }
            const adviceData = await adviceResponse.json();
            console.log("Financial advice fetched:", adviceData);
            setAdvice(adviceData.advice);

            console.log("Fetching investment recommendations...");
            const recommendationsResponse = await fetch('http://localhost:8000/investment_recommendations/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    income: parseFloat(formData.income),
                    expenses: parseFloat(formData.expenses),
                    goals: formData.goals,
                    risk_tolerance: formData.risk_tolerance
                })
            });
            if (!recommendationsResponse.ok) {
                throw new Error(`Investment recommendations fetch failed: ${recommendationsResponse.statusText}`);
            }
            const recommendationsData = await recommendationsResponse.json();
            console.log("Investment recommendations fetched:", recommendationsData);
            setRecommendations(recommendationsData.recommendations);

            console.log("Fetching market sentiment...");
            const sentimentResponse = await fetch(`http://localhost:8000/market_sentiment/${formData.sector}`);
            if (!sentimentResponse.ok) {
                throw new Error(`Market sentiment fetch failed: ${sentimentResponse.statusText}`);
            }
            const sentimentData = await sentimentResponse.json();
            console.log("Market sentiment fetched:", sentimentData);
            setSentiment(sentimentData);
        } catch (error) {
            console.error('Error fetching API data:', error);
            setError('Failed to fetch API data. Please try again later.');
            setLoading(false);
            return;
        }

        setLoading(false);
    };

    useEffect(() => {
        if (formData.income && formData.expenses) {
            // Destroy the previous budget chart if it exists
            if (budgetChartRef.current) {
                budgetChartRef.current.destroy();
                budgetChartRef.current = null;
            }

            try {
                console.log("Rendering budget pie chart...");
                const ctxBudget = document.getElementById('budgetChart');
                if (ctxBudget) {
                    budgetChartRef.current = new Chart(ctxBudget, {
                        type: 'pie',
                        data: {
                            labels: ['Expenses', 'Disposable Income'],
                            datasets: [{
                                data: [formData.expenses, formData.income - formData.expenses],
                                backgroundColor: ['#FF6384', '#36A2EB']
                            }]
                        }
                    });
                } else {
                    console.warn("Budget chart canvas not found.");
                }
            } catch (error) {
                console.error('Error rendering budget chart:', error);
            }
        }

        // Cleanup on unmount
        return () => {
            if (budgetChartRef.current) {
                budgetChartRef.current.destroy();
                budgetChartRef.current = null;
            }
        };
    }, [formData.income, formData.expenses]);

    useEffect(() => {
        if (sentiment) {
            // Destroy the previous sentiment chart if it exists
            if (sentimentChartRef.current) {
                sentimentChartRef.current.destroy();
                sentimentChartRef.current = null;
            }

            try {
                console.log("Rendering sentiment bar chart...");
                const ctxSentiment = document.getElementById('sentimentChart');
                if (ctxSentiment) {
                    sentimentChartRef.current = new Chart(ctxSentiment, {
                        type: 'bar',
                        data: {
                            labels: ['News Sentiment', 'Social Sentiment'],
                            datasets: [{
                                label: 'Sentiment',
                                data: [
                                    sentiment.news_sentiment === 'POSITIVE' ? 1 : sentiment.news_sentiment === 'NEGATIVE' ? -1 : 0,
                                    sentiment.social_sentiment === 'POSITIVE' ? 1 : sentiment.social_sentiment === 'NEGATIVE' ? -1 : 0
                                ],
                                backgroundColor: ['#FF6384', '#36A2EB']
                            }]
                        },
                        options: {
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        callback: function(value) {
                                            if (value === 1) return 'POSITIVE';
                                            if (value === -1) return 'NEGATIVE';
                                            return 'NEUTRAL';
                                        }
                                    }
                                }
                            }
                        }
                    });
                } else {
                    console.warn("Sentiment chart canvas not found.");
                }
            } catch (error) {
                console.error('Error rendering sentiment chart:', error);
            }
        }

        // Cleanup on unmount
        return () => {
            if (sentimentChartRef.current) {
                sentimentChartRef.current.destroy();
                sentimentChartRef.current = null;
            }
        };
    }, [sentiment]);

    return (
        <div className="App">
            <h1>FinWiseAI</h1>
            <form onSubmit={handleSubmit}>
                <input type="number" name="income" placeholder="Annual Income" onChange={handleChange} required />
                <input type="number" name="expenses" placeholder="Annual Expenses" onChange={handleChange} required />
                <input type="text" name="goals" placeholder="Financial Goals" onChange={handleChange} required />
                <select name="risk_tolerance" onChange={handleChange} required>
                    <option value="">Select Risk Tolerance</option>
                    <option value="Conservative">Conservative</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Aggressive">Aggressive</option>
                </select>
                <input type="text" name="sector" placeholder="Sector for Market Sentiment (e.g., tech)" onChange={handleChange} required />
                <button type="submit">Get Advice</button>
            </form>
            {loading && <p>Loading...</p>}
            {error && <p>{error}</p>}
            {advice && (
                <div>
                    <h2>Financial Advice</h2>
                    <p>{advice}</p>
                </div>
            )}
            {recommendations && (
                <div>
                    <h2>Investment Recommendations</h2>
                    <ul>
                        {recommendations.map((rec, index) => (
                            <li key={index}>
                                {rec.description} (Relevance Score: {rec.relevance_score.toFixed(2)})
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            {sentiment && (
                <div>
                    <h2>Market Sentiment for {formData.sector}</h2>
                    <p>News Sentiment: {sentiment.news_sentiment}</p>
                    <p>Social Sentiment: {sentiment.social_sentiment}</p>
                    <h3>News Articles</h3>
                    <ul>
                        {sentiment.news_articles.map((article, index) => (
                            <li key={index}>{article}</li>
                        ))}
                    </ul>
                    <h3>Tweets</h3>
                    <ul>
                        {sentiment.tweets.map((tweet, index) => (
                            <li key={index}>{tweet}</li>
                        ))}
                    </ul>
                </div>
            )}
            <div>
                <h2>Budget Breakdown</h2>
                <canvas id="budgetChart"></canvas>
            </div>
            {sentiment && (
                <div>
                    <h2>Sentiment Trends</h2>
                    <canvas id="sentimentChart"></canvas>
                </div>
            )}
        </div>
    );
}

export default App;