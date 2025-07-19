"""
Test suite for trading tools (crypto, forex, and news data).

This module tests all trading tools with real API calls using the Alpha Vantage API.
Make sure your ALPHA_VANTAGE_API_KEY is set in your .env file before running tests.
"""

import sys
import os
import json
import time
from datetime import datetime

# Add the src directory to the path so we can import our tools
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from forex_ai_agent.tools.crypto_data import crypto_api_connector
from forex_ai_agent.tools.forex_data import forex_data_fetcher
from forex_ai_agent.tools.news_data import news_sentiment_fetcher


def print_separator(title: str):
    """Print a nice separator for test sections"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_result(tool_name: str, result: str, success: bool = True):
    """Print test results in a formatted way"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"\n{status} - {tool_name}")
    print("-" * 40)
    
    try:
        # Try to parse and pretty print JSON
        data = json.loads(result)
        print(json.dumps(data, indent=2))
    except:
        # If not JSON, print as is
        print(result)


def test_crypto_data():
    """Test cryptocurrency data fetching"""
    print_separator("TESTING CRYPTO DATA TOOLS")
    
    # Test cases for crypto
    crypto_tests = [
        {"symbol": "BTC", "vs_currency": "USD", "name": "Bitcoin to USD"},
        {"symbol": "ETH", "vs_currency": "USD", "name": "Ethereum to USD"},
        {"symbol": "BTC", "vs_currency": "EUR", "name": "Bitcoin to EUR"},
    ]
    
    for test in crypto_tests:
        print(f"\n🔍 Testing: {test['name']}")
        try:
            result = crypto_api_connector._run(
                symbol=test["symbol"], 
                vs_currency=test["vs_currency"]
            )
            
            # Check if successful
            data = json.loads(result)
            success = data.get("success", False)
            print_result(f"Crypto: {test['name']}", result, success)
            
            # Add delay to respect API rate limits
            time.sleep(2)
            
        except Exception as e:
            print_result(f"Crypto: {test['name']}", f"Error: {str(e)}", False)


def test_forex_data():
    """Test forex data fetching"""
    print_separator("TESTING FOREX DATA TOOLS")
    
    # Test cases for forex
    forex_tests = [
        {"from_currency": "EUR", "to_currency": "USD", "name": "EUR/USD"},
        {"from_currency": "GBP", "to_currency": "USD", "name": "GBP/USD"},
        {"from_currency": "USD", "to_currency": "JPY", "name": "USD/JPY"},
        {"from_currency": "AUD", "to_currency": "USD", "name": "AUD/USD"},
    ]
    
    for test in forex_tests:
        print(f"\n🔍 Testing: {test['name']}")
        try:
            result = forex_data_fetcher._run(
                from_currency=test["from_currency"], 
                to_currency=test["to_currency"]
            )
            
            # Check if successful
            data = json.loads(result)
            success = data.get("success", False)
            print_result(f"Forex: {test['name']}", result, success)
            
            # Add delay to respect API rate limits
            time.sleep(2)
            
        except Exception as e:
            print_result(f"Forex: {test['name']}", f"Error: {str(e)}", False)


def test_news_data():
    """Test news and sentiment data fetching"""
    print_separator("TESTING NEWS & SENTIMENT TOOLS")
    
    # Test cases for news
    news_tests = [
        {
            "tickers": "CRYPTO:BTC",
            "topics": None,
            "limit": 5,
            "name": "Bitcoin News"
        },
        {
            "tickers": "FOREX:USD",
            "topics": None,
            "limit": 5,
            "name": "USD Forex News"
        },
        {
            "tickers": None,
            "topics": "blockchain",
            "limit": 5,
            "name": "Blockchain Topic News"
        },
        {
            "tickers": None,
            "topics": "financial_markets",
            "limit": 5,
            "name": "Financial Markets News"
        },
        {
            "tickers": "CRYPTO:BTC,FOREX:USD",
            "topics": None,
            "limit": 3,
            "name": "Combined BTC + USD News"
        }
    ]
    
    for test in news_tests:
        print(f"\n🔍 Testing: {test['name']}")
        try:
            result = news_sentiment_fetcher._run(
                tickers=test["tickers"],
                topics=test["topics"],
                limit=test["limit"],
                sort="LATEST"
            )
            
            # Check if successful
            data = json.loads(result)
            success = data.get("success", False)
            print_result(f"News: {test['name']}", result, success)
            
            # Add longer delay for news API (more complex)
            time.sleep(3)
            
        except Exception as e:
            print_result(f"News: {test['name']}", f"Error: {str(e)}", False)


def test_api_key_validation():
    """Test API key validation"""
    print_separator("TESTING API KEY VALIDATION")
    
    # Check if API key is available
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if api_key:
        print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
        print(f"📊 API Key length: {len(api_key)} characters")
        return True
    else:
        print("❌ ALPHA_VANTAGE_API_KEY not found in environment variables")
        print("💡 Please add your API key to the .env file")
        return False


def run_comprehensive_test():
    """Run all tests in sequence"""
    print_separator("FOREX AI AGENT - TRADING TOOLS TEST SUITE")
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check API key first
    if not test_api_key_validation():
        print("\n❌ Cannot proceed without API key. Exiting...")
        return
    
    print("\n⚠️  Note: This will make real API calls to Alpha Vantage")
    print("⚠️  Free tier has 25 requests/day limit")
    print("⚠️  Tests include delays to respect rate limits")
    
    try:
        # Run all tests
        test_crypto_data()
        test_forex_data() 
        test_news_data()
        
        print_separator("TEST SUITE COMPLETED")
        print("✅ All tests completed successfully!")
        print(f"🕐 Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {str(e)}")


def quick_test():
    """Run a quick test with minimal API calls"""
    print_separator("QUICK TEST - MINIMAL API CALLS")
    
    if not test_api_key_validation():
        return
    
    print("\n🚀 Running quick test (3 API calls total)...")
    
    # Test one of each tool
    try:
        print("\n1️⃣ Testing Crypto Tool (BTC/USD)...")
        crypto_result = crypto_api_connector._run("BTC", "USD")
        crypto_data = json.loads(crypto_result)
        print(f"   Result: {'✅ Success' if crypto_data.get('success') else '❌ Failed'}")
        time.sleep(2)
        
        print("\n2️⃣ Testing Forex Tool (EUR/USD)...")
        forex_result = forex_data_fetcher._run("EUR", "USD")
        forex_data = json.loads(forex_result)
        print(f"   Result: {'✅ Success' if forex_data.get('success') else '❌ Failed'}")
        time.sleep(2)
        
        print("\n3️⃣ Testing News Tool (Bitcoin news)...")
        news_result = news_sentiment_fetcher._run(tickers="CRYPTO:BTC", limit=2)
        news_data = json.loads(news_result)
        print(f"   Result: {'✅ Success' if news_data.get('success') else '❌ Failed'}")
        
        print("\n✅ Quick test completed!")
        
    except Exception as e:
        print(f"\n❌ Quick test failed: {str(e)}")


if __name__ == "__main__":
    print("🔧 Forex AI Agent - Trading Tools Test Suite")
    print("\nChoose test mode:")
    print("1. Quick Test (3 API calls)")
    print("2. Comprehensive Test (15+ API calls)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        quick_test()
    elif choice == "2":
        run_comprehensive_test()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice. Running quick test by default...")
        quick_test()