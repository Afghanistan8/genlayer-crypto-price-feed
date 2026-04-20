# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

"""
GenLayer Secure API Key Contract
==================================
This Intelligent Contract demonstrates the secure API key pattern.

The contract calls a proxy server instead of the real API directly.
The proxy server holds the API key privately on the server side.

SECURITY MODEL:
- Contract code is PUBLIC (anyone can read it on-chain)
- Proxy server is PRIVATE (only you control it)
- API keys are stored in proxy's .env file (never on-chain)
- PROXY_SECRET prevents unauthorized access to your proxy

SETUP:
1. Deploy proxy_server.py to your server
2. Set your PROXY_URL to your deployed server URL
3. Set your PROXY_SECRET to match the server's secret
4. Deploy this contract to GenLayer Studio
"""

from genlayer import *
import json
import typing

# ============================================================
# CONFIGURATION
# Replace PROXY_URL with your actual deployed proxy server URL
# The proxy secret must match what's in your .env file
# ============================================================
PROXY_URL = "https://your-proxy-server.com"
PROXY_SECRET = "your-secret-password-here"


class SecureAPIContract(gl.Contract):
    # Weather storage
    last_city: str
    last_temperature: str
    last_condition: str
    last_humidity: str

    # News storage
    last_news_topic: str
    last_news_titles: str

    # Stock storage
    last_symbol: str
    last_stock_price: str
    last_stock_change: str

    def __init__(self):
        self.last_city = ""
        self.last_temperature = ""
        self.last_condition = ""
        self.last_humidity = ""
        self.last_news_topic = ""
        self.last_news_titles = ""
        self.last_symbol = ""
        self.last_stock_price = ""
        self.last_stock_change = ""

    # ============================================================
    # SECURE WEATHER FETCH
    # Calls proxy → proxy calls OpenWeatherMap with secret key
    # ============================================================
    @gl.public.write
    def get_secure_weather(self, city: str) -> typing.Any:
        proxy_url = f"{PROXY_URL}/weather/{city}"

        def fetch() -> str:
            # Send request to proxy with secret header
            response = gl.nondet.web.request(
                proxy_url,
                method="GET",
                headers={
                    "X-Proxy-Secret": PROXY_SECRET,
                    "Accept": "application/json"
                }
            )
            if response.status_code == 401:
                raise gl.UserError("Proxy authentication failed")
            if response.status_code != 200:
                raise gl.UserError(f"Proxy error: {response.status_code}")

            data = json.loads(response.body.decode("utf-8"))
            return json.dumps({
                "temperature": str(data["temperature"]),
                "condition": data["condition"],
                "humidity": str(data["humidity"])
            }, sort_keys=True)

        result = gl.eq_principle.prompt_comparative(
            fetch,
            principle="Temperature must be within 1 degree. Condition and humidity must be the same."
        )

        parsed = json.loads(result)
        self.last_city = city
        self.last_temperature = parsed["temperature"]
        self.last_condition = parsed["condition"]
        self.last_humidity = parsed["humidity"]

    # ============================================================
    # SECURE NEWS FETCH
    # Calls proxy → proxy calls NewsAPI with secret key
    # ============================================================
    @gl.public.write
    def get_secure_news(self, topic: str) -> typing.Any:
        proxy_url = f"{PROXY_URL}/news/{topic}"

        def fetch() -> str:
            response = gl.nondet.web.request(
                proxy_url,
                method="GET",
                headers={
                    "X-Proxy-Secret": PROXY_SECRET,
                    "Accept": "application/json"
                }
            )
            if response.status_code == 401:
                raise gl.UserError("Proxy authentication failed")
            if response.status_code != 200:
                raise gl.UserError(f"Proxy error: {response.status_code}")

            data = json.loads(response.body.decode("utf-8"))
            titles = [a["title"] for a in data.get("articles", [])[:5]]

            # Use LLM to analyze sentiment of news titles
            prompt = f"""
            Analyze the sentiment of these news headlines about "{topic}":
            {chr(10).join(f"- {t}" for t in titles)}

            Return ONLY valid JSON:
            {{"sentiment": "Positive", "titles": {json.dumps(titles)}}}
            """
            result = gl.nondet.exec_prompt(prompt)
            clean = result.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return clean.strip()

        result = gl.eq_principle.prompt_comparative(
            fetch,
            principle="Sentiment must be identical. Titles must be the same articles."
        )

        parsed = json.loads(result)
        self.last_news_topic = topic
        self.last_news_titles = json.dumps(parsed.get("titles", []))

    # ============================================================
    # SECURE STOCK PRICE FETCH
    # Calls proxy → proxy calls Alpha Vantage with secret key
    # ============================================================
    @gl.public.write
    def get_secure_stock(self, symbol: str) -> typing.Any:
        proxy_url = f"{PROXY_URL}/stock/{symbol}"

        def fetch() -> str:
            response = gl.nondet.web.request(
                proxy_url,
                method="GET",
                headers={
                    "X-Proxy-Secret": PROXY_SECRET,
                    "Accept": "application/json"
                }
            )
            if response.status_code == 401:
                raise gl.UserError("Proxy authentication failed")
            if response.status_code != 200:
                raise gl.UserError(f"Proxy error: {response.status_code}")

            data = json.loads(response.body.decode("utf-8"))
            return json.dumps({
                "price": data["price"],
                "change": data["change"],
                "change_percent": data["change_percent"]
            }, sort_keys=True)

        result = gl.eq_principle.prompt_comparative(
            fetch,
            principle="Price must be within 1% of each other. Change percent must be the same."
        )

        parsed = json.loads(result)
        self.last_symbol = symbol
        self.last_stock_price = parsed["price"]
        self.last_stock_change = parsed["change_percent"]

    # ============================================================
    # READ METHODS
    # ============================================================
    @gl.public.view
    def read_weather(self) -> dict:
        return {
            "city": self.last_city,
            "temperature_c": self.last_temperature,
            "condition": self.last_condition,
            "humidity_%": self.last_humidity
        }

    @gl.public.view
    def read_news(self) -> dict:
        return {
            "topic": self.last_news_topic,
            "recent_headlines": json.loads(self.last_news_titles) if self.last_news_titles else []
        }

    @gl.public.view
    def read_stock(self) -> dict:
        return {
            "symbol": self.last_symbol,
            "price_usd": self.last_stock_price,
            "change_%": self.last_stock_change
        }
