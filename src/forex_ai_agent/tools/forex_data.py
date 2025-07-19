"""
Forex market data tools.

This module provides tools for fetching real-time forex
market data using Alpha Vantage API.
"""

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import json
import os
from datetime import datetime


class ForexDataInput(BaseModel):
    """Input schema for forex data fetcher."""
    from_currency: str = Field(..., description="Base currency (e.g., EUR, GBP, USD)")
    to_currency: str = Field(..., description="Quote currency (e.g., USD, EUR, JPY)")


class ForexDataFetcher(BaseTool):
    name: str = "forex_data_fetcher"
    description: str = (
        "Fetch real-time forex market data using Alpha Vantage API. "
        "Provides exchange rates, bid/ask prices, and market timing for major currency pairs."
    )
    args_schema: Type[BaseModel] = ForexDataInput

    def _run(self, from_currency: str, to_currency: str) -> str:
        """Fetch forex data from Alpha Vantage"""
        try:
            api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
            if not api_key:
                return json.dumps({
                    "error": "ALPHA_VANTAGE_API_KEY not found in environment variables",
                    "success": False,
                    "message": "Get your free API key from: https://www.alphavantage.co/support/#api-key"
                })

            # Alpha Vantage FX endpoint
            base_url = "https://www.alphavantage.co/query"
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": from_currency.upper(),
                "to_currency": to_currency.upper(),
                "apikey": api_key
            }

            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                return json.dumps({
                    "error": data["Error Message"],
                    "success": False,
                    "message": f"Invalid currency pair: {from_currency}/{to_currency}"
                })
            
            if "Note" in data:
                return json.dumps({
                    "error": "API rate limit exceeded",
                    "success": False,
                    "message": "Alpha Vantage free tier: 25 requests/day. Upgrade for more requests."
                })

            # Parse the forex response
            if "Realtime Currency Exchange Rate" in data:
                rate_data = data["Realtime Currency Exchange Rate"]
                
                # Calculate spread and spread percentage
                bid_price = float(rate_data["8. Bid Price"])
                ask_price = float(rate_data["9. Ask Price"])
                spread = ask_price - bid_price
                spread_percentage = (spread / bid_price) * 100 if bid_price > 0 else 0
                
                # Determine market session
                current_time = datetime.now()
                market_status = self._get_forex_market_status(current_time)
                
                result = {
                    "success": True,
                    "symbol": f"{from_currency}/{to_currency}",
                    "current_price": float(rate_data["5. Exchange Rate"]),
                    "bid_price": bid_price,
                    "ask_price": ask_price,
                    "spread": round(spread, 6),
                    "spread_percentage": round(spread_percentage, 4),
                    "timestamp": rate_data["6. Last Refreshed"],
                    "timezone": rate_data["7. Time Zone"],
                    "market_status": market_status,
                    "data_source": "Alpha Vantage",
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
                "success": False,
                "message": "Check your internet connection"
            })
        except Exception as e:
            return json.dumps({
                "error": f"Forex API error: {str(e)}",
                "success": False
            })

    def _get_forex_market_status(self, current_time: datetime) -> str:
        """Determine forex market status based on current time (UTC)"""
        # Forex market is open 24/5 (Monday 00:00 UTC to Friday 22:00 UTC)
        weekday = current_time.weekday()  # 0=Monday, 6=Sunday
        hour = current_time.hour
        
        if weekday == 6:  # Sunday
            return "closed"
        elif weekday == 5:  # Saturday
            return "closed"
        elif weekday == 0 and hour < 0:  # Monday before market open (theoretical)
            return "pre_market"
        elif weekday == 4 and hour >= 22:  # Friday after 22:00 UTC
            return "closed"
        else:
            return "open"


# Create tool instance
forex_data_fetcher = ForexDataFetcher()