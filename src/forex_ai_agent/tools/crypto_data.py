"""
Cryptocurrency market data tools.

This module provides tools for fetching real-time cryptocurrency
market data using Alpha Vantage API.
"""

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import json
import os
from datetime import datetime


class CryptoAPIInput(BaseModel):
    """Input schema for crypto API connector."""
    symbol: str = Field(..., description="Crypto symbol (e.g., BTC, ETH, ADA)")
    vs_currency: str = Field(default="USD", description="Quote currency (USD, EUR, etc.)")


class CryptoAPIConnector(BaseTool):
    name: str = "crypto_api_connector"
    description: str = (
        "Fetch real-time cryptocurrency market data using Alpha Vantage API. "
        "Provides current price, market cap, volume, and price changes for major cryptocurrencies."
    )
    args_schema: Type[BaseModel] = CryptoAPIInput

    def _run(self, symbol: str, vs_currency: str = "USD") -> str:
        """Fetch cryptocurrency data from Alpha Vantage"""
        try:
            api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
            if not api_key:
                return json.dumps({
                    "error": "ALPHA_VANTAGE_API_KEY not found in environment variables",
                    "success": False,
                    "message": "Please add your Alpha Vantage API key to .env file"
                })

            # Alpha Vantage Digital Currency endpoint
            base_url = "https://www.alphavantage.co/query"
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": symbol,
                "to_currency": vs_currency,
                "apikey": api_key
            }

            response = requests.get(base_url, params=params, timeout=10)
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

            # Parse the response
            if "Realtime Currency Exchange Rate" in data:
                rate_data = data["Realtime Currency Exchange Rate"]
                
                # Calculate spread for crypto trading
                bid_price = float(rate_data["8. Bid Price"])
                ask_price = float(rate_data["9. Ask Price"])
                spread = ask_price - bid_price
                spread_percentage = (spread / bid_price) * 100 if bid_price > 0 else 0
                
                result = {
                    "success": True,
                    "symbol": f"{symbol}/{vs_currency}",
                    "current_price": float(rate_data["5. Exchange Rate"]),
                    "bid_price": bid_price,
                    "ask_price": ask_price,
                    "spread": round(spread, 8),  # More precision for crypto
                    "spread_percentage": round(spread_percentage, 4),
                    "timestamp": rate_data["6. Last Refreshed"],
                    "timezone": rate_data["7. Time Zone"],
                    "data_source": "Alpha Vantage",
                    "market_status": "open",  # Crypto markets are always open (24/7)
                    "pair_info": {
                        "from_currency": rate_data["1. From_Currency Code"],
                        "from_currency_name": rate_data["2. From_Currency Name"],
                        "to_currency": rate_data["3. To_Currency Code"],
                        "to_currency_name": rate_data["4. To_Currency Name"]
                    }
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
                "success": False
            })
        except Exception as e:
            return json.dumps({
                "error": f"Crypto API error: {str(e)}",
                "success": False
            })


# Create tool instance
crypto_api_connector = CryptoAPIConnector()