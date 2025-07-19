"""
Market news and sentiment data tools.

This module provides tools for fetching real-time market news and sentiment
data using Alpha Vantage News & Sentiment API for forex and crypto pairs.
"""

from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import requests
import json
import os
from datetime import datetime


class NewsDataInput(BaseModel):
    """Input schema for news and sentiment data fetcher."""
    tickers: Optional[str] = Field(
        default=None, 
        description="Comma-separated tickers (e.g., 'CRYPTO:BTC,FOREX:USD' or 'CRYPTO:ETH')"
    )
    topics: Optional[str] = Field(
        default=None,
        description="News topics: blockchain, earnings, ipo, financial_markets, economy_fiscal, economy_monetary, technology, etc."
    )
    limit: int = Field(default=50, description="Number of articles to return (max 1000)")
    sort: str = Field(default="LATEST", description="Sort order: LATEST, EARLIEST, or RELEVANCE")


class NewsAndSentimentFetcher(BaseTool):
    name: str = "news_sentiment_fetcher"
    description: str = (
        "Fetch real-time market news and sentiment data for forex and crypto pairs using Alpha Vantage. "
        "Provides news articles with sentiment analysis for trading pairs like CRYPTO:BTC, FOREX:USD, etc. "
        "Can filter by topics like blockchain, financial_markets, economy_monetary for comprehensive market analysis."
    )
    args_schema: Type[BaseModel] = NewsDataInput

    def _run(
        self, 
        tickers: Optional[str] = None, 
        topics: Optional[str] = None,
        limit: int = 50,
        sort: str = "LATEST"
    ) -> str:
        """Fetch news and sentiment data from Alpha Vantage"""
        try:
            api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
            if not api_key:
                return json.dumps({
                    "error": "ALPHA_VANTAGE_API_KEY not found in environment variables",
                    "success": False,
                    "message": "Please add your Alpha Vantage API key to .env file"
                })

            # Alpha Vantage News & Sentiment endpoint
            base_url = "https://www.alphavantage.co/query"
            params = {
                "function": "NEWS_SENTIMENT",
                "apikey": api_key,
                "limit": min(limit, 1000),  # Cap at 1000 as per API limit
                "sort": sort.upper()
            }

            # Add optional parameters if provided
            if tickers:
                params["tickers"] = tickers
            if topics:
                params["topics"] = topics

            response = requests.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                return json.dumps({
                    "error": data["Error Message"],
                    "success": False
                })
            
            if "Note" in data:
                return json.dumps({
                    "error": "API rate limit exceeded",
                    "success": False,
                    "message": "Alpha Vantage free tier: 25 requests/day limit reached"
                })

            # Parse the news response
            if "feed" in data:
                articles = data["feed"]
                
                # Process and structure the news data
                processed_articles = []
                for article in articles[:limit]:  # Respect the limit parameter
                    processed_article = {
                        "title": article.get("title", ""),
                        "url": article.get("url", ""),
                        "time_published": article.get("time_published", ""),
                        "authors": article.get("authors", []),
                        "summary": article.get("summary", ""),
                        "source": article.get("source", ""),
                        "category_within_source": article.get("category_within_source", ""),
                        "overall_sentiment_score": article.get("overall_sentiment_score", 0),
                        "overall_sentiment_label": article.get("overall_sentiment_label", "Neutral"),
                        "ticker_sentiment": article.get("ticker_sentiment", [])
                    }
                    processed_articles.append(processed_article)
                
                # Calculate summary statistics
                sentiment_scores = [
                    float(article.get("overall_sentiment_score", 0)) 
                    for article in articles[:limit]
                ]
                
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
                
                # Count sentiment labels
                sentiment_counts = {}
                for article in articles[:limit]:
                    label = article.get("overall_sentiment_label", "Neutral")
                    sentiment_counts[label] = sentiment_counts.get(label, 0) + 1
                
                result = {
                    "success": True,
                    "query_info": {
                        "tickers": tickers,
                        "topics": topics,
                        "sort": sort,
                        "limit": limit,
                        "articles_returned": len(processed_articles)
                    },
                    "sentiment_summary": {
                        "average_sentiment_score": round(avg_sentiment, 4),
                        "sentiment_distribution": sentiment_counts,
                        "market_mood": self._interpret_sentiment(avg_sentiment)
                    },
                    "articles": processed_articles,
                    "data_source": "Alpha Vantage News & Sentiment",
                    "timestamp": datetime.now().isoformat()
                }
                
                return json.dumps(result, indent=2)
            else:
                return json.dumps({
                    "error": "Unexpected API response format",
                    "success": False,
                    "raw_response": data
                })

        except requests.exceptions.RequestException as e:
            return json.dumps({
                "error": f"Network error: {str(e)}",
                "success": False,
                "message": "Check your internet connection"
            })
        except Exception as e:
            return json.dumps({
                "error": f"News API error: {str(e)}",
                "success": False
            })

    def _interpret_sentiment(self, avg_score: float) -> str:
        """Interpret average sentiment score into market mood"""
        if avg_score >= 0.15:
            return "Bullish"
        elif avg_score <= -0.15:
            return "Bearish"
        elif avg_score > 0:
            return "Slightly Bullish"
        elif avg_score < 0:
            return "Slightly Bearish"
        else:
            return "Neutral"


# Create tool instance
news_sentiment_fetcher = NewsAndSentimentFetcher()