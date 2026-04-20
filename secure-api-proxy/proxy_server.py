"""
GenLayer Secure API Key Proxy Server
=====================================
This Flask server acts as a secure middleman between GenLayer
Intelligent Contracts and external APIs that require API keys.

HOW IT WORKS:
- The API key is stored ONLY on this server (never in the contract)
- GenLayer contracts call THIS server instead of the real API
- The server adds the API key and forwards the request
- The contract code is public but the key remains private

SETUP:
1. Install dependencies: pip install flask requests python-dotenv
2. Create a .env file with your API keys (see .env.example)
3. Run the server: python proxy_server.py
4. The server runs on http://localhost:5000

DEPLOYMENT:
- Deploy to any cloud server (Railway, Render, Heroku, VPS)
- Your GenLayer contract calls your deployed server URL
- The API key never appears in contract code
"""

from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv
from functools import wraps

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# ============================================================
# CONFIGURATION
# Store all API keys in environment variables, NEVER in code
# ============================================================
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
PROXY_SECRET = os.getenv("PROXY_SECRET", "genlayer-proxy-secret")

# ============================================================
# SECURITY MIDDLEWARE
# Only allow requests that include the proxy secret header
# This prevents unauthorized access to your proxy
# ============================================================
def require_proxy_secret(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        secret = request.headers.get("X-Proxy-Secret")
        if secret != PROXY_SECRET:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# ============================================================
# HEALTH CHECK
# ============================================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "running",
        "message": "GenLayer Secure API Proxy is active",
        "endpoints": [
            "/weather/<city>",
            "/news/<topic>",
            "/stock/<symbol>"
        ]
    })


# ============================================================
# WEATHER ENDPOINT
# Wraps OpenWeatherMap API (requires API key)
# Contract calls: GET /weather/Lagos
# ============================================================
@app.route("/weather/<city>", methods=["GET"])
@require_proxy_secret
def get_weather(city):
    if not OPENWEATHER_API_KEY:
        return jsonify({"error": "Weather API key not configured"}), 500

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,  # Key added HERE, not in contract
            "units": "metric"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": data.get("message", "API error")}), response.status_code

        # Return only what the contract needs
        return jsonify({
            "city": city,
            "temperature": data["main"]["temp"],
            "condition": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "feels_like": data["main"]["feels_like"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# NEWS SENTIMENT ENDPOINT
# Wraps NewsAPI (requires API key)
# Contract calls: GET /news/bitcoin
# ============================================================
@app.route("/news/<topic>", methods=["GET"])
@require_proxy_secret
def get_news(topic):
    if not NEWS_API_KEY:
        return jsonify({"error": "News API key not configured"}), 500

    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": topic,
            "apiKey": NEWS_API_KEY,  # Key added HERE, not in contract
            "pageSize": 10,
            "sortBy": "publishedAt",
            "language": "en"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": data.get("message", "API error")}), response.status_code

        # Return only titles for sentiment analysis
        articles = [
            {
                "title": a["title"],
                "source": a["source"]["name"]
            }
            for a in data.get("articles", [])[:10]
            if a.get("title")
        ]

        return jsonify({
            "topic": topic,
            "articles": articles,
            "count": len(articles)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# STOCK PRICE ENDPOINT
# Wraps Alpha Vantage API (requires API key)
# Contract calls: GET /stock/AAPL
# ============================================================
@app.route("/stock/<symbol>", methods=["GET"])
@require_proxy_secret
def get_stock(symbol):
    if not ALPHA_VANTAGE_KEY:
        return jsonify({"error": "Stock API key not configured"}), 500

    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_KEY,  # Key added HERE, not in contract
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        quote = data.get("Global Quote", {})
        if not quote:
            return jsonify({"error": "Symbol not found"}), 404

        return jsonify({
            "symbol": symbol,
            "price": quote.get("05. price", "0"),
            "change": quote.get("09. change", "0"),
            "change_percent": quote.get("10. change percent", "0%"),
            "volume": quote.get("06. volume", "0")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# RATE LIMITING TRACKER (simple in-memory)
# Tracks requests per IP to prevent abuse
# ============================================================
request_counts = {}

@app.before_request
def track_requests():
    ip = request.remote_addr
    request_counts[ip] = request_counts.get(ip, 0) + 1
    if request_counts[ip] > 100:
        return jsonify({"error": "Rate limit exceeded"}), 429


if __name__ == "__main__":
    print("=" * 50)
    print("GenLayer Secure API Proxy Server")
    print("=" * 50)
    print(f"Weather API: {'✓ Configured' if OPENWEATHER_API_KEY else '✗ Not configured'}")
    print(f"News API:    {'✓ Configured' if NEWS_API_KEY else '✗ Not configured'}")
    print(f"Stock API:   {'✓ Configured' if ALPHA_VANTAGE_KEY else '✗ Not configured'}")
    print("=" * 50)
    print("Server running on http://localhost:5000")
    app.run(debug=False, host="0.0.0.0", port=5000)
