# GenLayer Crypto Price Feed Library

A GenLayer Intelligent Contract that fetches live crypto prices 
from Binance API directly on-chain using AI validators.

## Features
- Fetch single coin price using `get_price`
- Fetch top 5 coins at once using `get_top5_prices`
- Prices validated by AI validators using `prompt_comparative`
- Supports: BTC, ETH, BNB, SOL, XRP

## How It Works
This Intelligent Contract uses GenLayer's `gl.nondet.web.get()` 
to call Binance's public API directly on-chain. Multiple AI 
validators independently fetch the prices and reach consensus 
using the `prompt_comparative` equivalence principle with a 2% 
tolerance — allowing agreement even with real-time price fluctuations.

## Functions
| Function | Type | Description |
|---|---|---|
| `get_price(symbol)` | Write | Fetch price of one coin e.g. BTC |
| `get_top5_prices()` | Write | Fetch BTC, ETH, BNB, SOL, XRP |
| `read_price()` | Read | Read last single coin price |
| `read_all_prices()` | Read | Read all 5 coin prices |

## Usage
Deploy on [GenLayer Studio](https://studio.genlayer.com) and call:
- `get_top5_prices()` to fetch all prices
- `read_all_prices()` to read stored prices

## Built For
GenLayer Tools & Infrastructure Bounty Task


---

# GenLayer Weather Feed Library

A GenLayer Intelligent Contract that fetches live weather data
from Open-Meteo API directly on-chain using AI validators.

## Features
- Fetch weather for any city using coordinates
- Fetch 5 major cities at once
- No API key needed
- Supports: Weather condition and Humidity

## Weather Data
- **Condition** — Clear sky, Partly cloudy, Rain, etc.
- **Humidity** — Percentage relative humidity

## Cities Supported
Lagos, London, New York, Tokyo, Dubai

## Functions
| Function | Type | Description |
|---|---|---|
| `get_weather(city, lat, lon)` | Write | Fetch any city weather |
| `get_cities_weather()` | Write | Fetch all 5 cities |
| `read_weather()` | Read | Read last city result |
| `read_cities_weather()` | Read | Read all 5 cities |

## Usage
Deploy on [GenLayer Studio](https://studio.genlayer.com) and call:
- `get_cities_weather()` to fetch all cities
- `read_cities_weather()` to read stored results

---

# GenLayer Hacker News Sentiment Library

Analyzes sentiment of Hacker News stories using GenLayer's AI validators.

## Features
- Analyze sentiment for any topic
- Analyze today's top HN stories
- Uses LLM reasoning for intelligent sentiment classification
- Returns: Positive / Negative / Neutral + summary

## Functions
| Function | Type | Description |
|---|---|---|
| `analyze_topic(topic)` | Write | Analyze any topic e.g. bitcoin |
| `analyze_top_stories()` | Write | Analyze today's top stories |
| `read_topic_sentiment()` | Read | Read topic result |
| `read_top_stories_sentiment()` | Read | Read top stories result |

## Built For
GenLayer Tools & Infrastructure Bounty Task

---

# GenLayer Secure API Key Proxy

A full proxy server pattern for keeping API keys private
while allowing GenLayer Intelligent Contracts to use them securely.

## The Problem
Blockchain contract code is public — anyone can read it.
You cannot put API keys directly in a contract.

## The Solution

## Files
| File | Description |
|---|---|
| `proxy_server.py` | Flask server that holds API keys privately |
| `secure_api_contract.py` | GenLayer contract that calls the proxy |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for storing API keys |

## APIs Supported
| API | Endpoint | Key Required |
|---|---|---|
| OpenWeatherMap | `/weather/<city>` | Yes |
| NewsAPI | `/news/<topic>` | Yes |
| Alpha Vantage | `/stock/<symbol>` | Yes |

## How to Run the Proxy
1. Install: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your keys
3. Run: `python proxy_server.py`
4. Server starts at `http://localhost:5000`

## Security Features
- API keys stored in `.env` file only
- `X-Proxy-Secret` header authentication
- Rate limiting (100 requests per IP)
- Keys never appear in contract code

## Built For
GenLayer Tools & Infrastructure Bounty Task
