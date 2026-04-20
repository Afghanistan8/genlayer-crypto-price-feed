# GenLayer Tools & Infrastructure Libraries
## Complete Documentation & Usage Guide

A collection of Intelligent Contract libraries for GenLayer that enable
on-chain access to real-world data including crypto prices, weather,
and social media sentiment — all without oracles or API keys (where possible).

---

## Table of Contents
1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Library 1: Crypto Price Feed](#library-1-crypto-price-feed)
4. [Library 2: Weather Feed](#library-2-weather-feed)
5. [Library 3: Hacker News Sentiment](#library-3-hacker-news-sentiment)
6. [Deployment Guide](#deployment-guide)
7. [Common Patterns](#common-patterns)
8. [Troubleshooting](#troubleshooting)

---

## Overview

These libraries solve a core problem in blockchain development:
**smart contracts cannot see the outside world.**

GenLayer's Intelligent Contracts fix this by combining:
- `gl.nondet.web.get()` — to fetch real-world data from APIs
- `gl.nondet.exec_prompt()` — to reason about data using AI
- `gl.eq_principle.prompt_comparative()` — to reach consensus across validators

| Library | API Used | Key Feature |
|---|---|---|
| Crypto Price Feed | Binance (free) | Live BTC, ETH, BNB, SOL, XRP prices |
| Weather Feed | Open-Meteo (free, no key) | Weather condition & humidity |
| HN Sentiment | Hacker News + LLM | AI-powered sentiment analysis |

---

## How It Works

Every library follows the same 3-step pattern:

```
Step 1: FETCH
gl.nondet.web.get(api_url) 
→ Fetches live data from external API

Step 2: PROCESS  
json.loads(response.body.decode("utf-8"))
→ Parses the JSON response

Step 3: CONSENSUS
gl.eq_principle.prompt_comparative(fetch, principle="...")
→ Multiple AI validators agree on the result
```

### Why prompt_comparative?
Real-world data like prices and weather change every second.
`strict_eq` requires validators to get the exact same value —
impossible for live data. `prompt_comparative` uses an AI judge
that says "close enough" based on your defined principle (e.g. within 2%).

---

## Library 1: Crypto Price Feed

**File:** `crypto_price_feed.py`
**API:** Binance Public API (free, no key needed)
**Endpoint:** `https://api.binance.com/api/v3/ticker/price?symbol={SYMBOL}USDT`

### Functions

| Function | Type | Parameters | Returns |
|---|---|---|---|
| `get_price(symbol)` | Write | symbol: str e.g. "BTC" | Stores price on-chain |
| `get_top5_prices()` | Write | none | Stores BTC,ETH,BNB,SOL,XRP |
| `read_price()` | Read | none | `{"coin": "BTC", "price_usd": "75000"}` |
| `read_all_prices()` | Read | none | `{"BTC": "75000", "ETH": "2300", ...}` |

### Example Usage

**Fetch single coin:**
```
Function: get_price
Argument: BTC
→ Wait for FINALIZED + SUCCESS
→ Call read_price() to see result
```

**Fetch all 5 coins:**
```
Function: get_top5_prices
No arguments needed
→ Wait for FINALIZED + SUCCESS
→ Call read_all_prices() to see result
```

### Example Output
```json
{
  "BTC": "75101.94000000",
  "ETH": "2305.73000000",
  "BNB": "625.45000000",
  "SOL": "84.92000000",
  "XRP": "1.41430000"
}
```

### Supported Symbols
Any coin listed on Binance with a USDT pair:
`BTC`, `ETH`, `BNB`, `SOL`, `XRP`, `ADA`, `AVAX`, `DOGE`, `DOT`, `LINK`

### Key Code Pattern
```python
def fetch_all():
    btc = json.loads(gl.nondet.web.get(
        "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    ).body.decode("utf-8"))["price"]
    return json.dumps({"BTC": btc}, sort_keys=True)

result = gl.eq_principle.prompt_comparative(
    fetch_all,
    principle="Prices must be within 2% of each other."
)
```

---

## Library 2: Weather Feed

**File:** `weather_feed.py`
**API:** Open-Meteo (completely free, no API key needed)
**Endpoint:** `https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=weather_code,relative_humidity_2m`

### Functions

| Function | Type | Parameters | Returns |
|---|---|---|---|
| `get_weather(city, lat, lon)` | Write | city: str, latitude: str, longitude: str | Stores weather on-chain |
| `get_cities_weather()` | Write | none | Stores 5 cities weather |
| `read_weather()` | Read | none | `{"city": "Lagos", "condition": "...", "humidity_%": "85"}` |
| `read_cities_weather()` | Read | none | Weather for all 5 cities |

### Example Usage

**Fetch single city:**
```
Function: get_weather
Arguments:
  city: Lagos
  latitude: 6.5244
  longitude: 3.3792
→ Wait for FINALIZED + SUCCESS
→ Call read_weather() to see result
```

**Fetch all 5 cities:**
```
Function: get_cities_weather
No arguments needed
→ Wait for FINALIZED + SUCCESS
→ Call read_cities_weather() to see result
```

### City Coordinates Reference

| City | Latitude | Longitude |
|---|---|---|
| Lagos | 6.5244 | 3.3792 |
| London | 51.5074 | -0.1278 |
| New York | 40.7128 | -74.0060 |
| Tokyo | 35.6762 | 139.6503 |
| Dubai | 25.2048 | 55.2708 |
| Paris | 48.8566 | 2.3522 |
| Sydney | -33.8688 | 151.2093 |
| Nairobi | -1.2921 | 36.8219 |

### Weather Condition Codes (WMO Standard)

| Code | Condition |
|---|---|
| 0 | Clear sky |
| 1-3 | Partly cloudy |
| 45, 48 | Foggy |
| 51-55 | Drizzle |
| 61-65 | Rain |
| 71-75 | Snow |
| 80-82 | Showers |
| 95, 99 | Thunderstorm |

### Example Output
```json
{
  "Lagos":    {"condition": "Partly cloudy", "humidity_%": "85"},
  "London":   {"condition": "Overcast",      "humidity_%": "78"},
  "New York": {"condition": "Clear sky",     "humidity_%": "45"},
  "Tokyo":    {"condition": "Light rain",    "humidity_%": "90"},
  "Dubai":    {"condition": "Clear sky",     "humidity_%": "30"}
}
```

### Key Code Pattern
```python
def fetch():
    response = gl.nondet.web.get(api_url)
    data = json.loads(response.body.decode("utf-8"))
    code = int(data["current"]["weather_code"])
    humidity = str(data["current"]["relative_humidity_2m"])
    condition = get_condition_description(code)
    return json.dumps({"condition": condition, "humidity": humidity})

result = gl.eq_principle.prompt_comparative(
    fetch,
    principle="Condition must be same. Humidity within 5%."
)
```

---

## Library 3: Hacker News Sentiment

**File:** `hackernews_sentiment.py`
**API:** Hacker News (free, no key) + GenLayer LLM
**Endpoints:**
- Search: `https://hn.algolia.com/api/v1/search?query={topic}&tags=story`
- Top stories: `https://hacker-news.firebaseio.com/v0/topstories.json`
- Story details: `https://hacker-news.firebaseio.com/v0/item/{id}.json`

### Functions

| Function | Type | Parameters | Returns |
|---|---|---|---|
| `analyze_topic(topic)` | Write | topic: str e.g. "bitcoin" | Stores sentiment on-chain |
| `analyze_top_stories()` | Write | none | Stores top stories sentiment |
| `read_topic_sentiment()` | Read | none | `{"topic": "bitcoin", "sentiment": "Positive", ...}` |
| `read_top_stories_sentiment()` | Read | none | `{"sentiment": "Negative", "summary": "..."}` |

### Example Usage

**Analyze a topic:**
```
Function: analyze_topic
Argument: bitcoin
→ Wait for FINALIZED + SUCCESS
→ Call read_topic_sentiment() to see result
```

**Analyze top stories:**
```
Function: analyze_top_stories
No arguments needed
→ Wait for FINALIZED + SUCCESS
→ Call read_top_stories_sentiment() to see result
```

### Suggested Topics to Analyze
`bitcoin`, `ethereum`, `AI`, `openai`, `rust`, `python`,
`javascript`, `startup`, `security`, `climate`

### Example Output
```json
{
  "topic": "bitcoin",
  "sentiment": "Positive",
  "summary": "Community is optimistic about Bitcoin's 
               price milestone and institutional adoption.",
  "posts_analyzed": "10"
}
```

### How the AI Analysis Works
1. Contract fetches 10 HN stories about the topic
2. Extracts titles, points and comment counts
3. Sends to GenLayer's built-in LLM with a prompt
4. LLM returns Positive/Negative/Neutral + summary
5. Multiple validators run the same analysis
6. `prompt_comparative` ensures they agree on the sentiment

### Key Code Pattern
```python
def fetch_and_analyze() -> str:
    response = gl.nondet.web.get(search_url)
    data = json.loads(response.body.decode("utf-8"))
    stories = [f"- {h['title']} (points: {h['points']})" 
               for h in data["hits"][:10]]
    
    prompt = f"""
    Analyze sentiment of these HN stories about "{topic}":
    {chr(10).join(stories)}
    Return JSON: {{"sentiment": "Positive", "summary": "..."}}
    """
    result = gl.nondet.exec_prompt(prompt)
    return result

result = gl.eq_principle.prompt_comparative(
    fetch_and_analyze,
    principle="Sentiment classification must be identical."
)
```

---

## Deployment Guide

### Step 1 — Open GenLayer Studio
Go to [studio.genlayer.com](https://studio.genlayer.com)

### Step 2 — Create New Contract
Click **"New Contract.py"** tab at the top

### Step 3 — Upload Contract File
Upload any of the 3 library files

### Step 4 — Deploy
Click **Deploy** and wait for **FINALIZED + SUCCESS**

### Step 5 — Write Data
Call any write method (e.g. `get_price`, `get_weather`, `analyze_topic`)
and wait for **FINALIZED + SUCCESS**

### Step 6 — Read Data
Set State dropdown to **Finalized** then call any read method

---

## Common Patterns

### Pattern 1: Fetch + Store
```python
def fetch() -> str:
    response = gl.nondet.web.get(url)
    data = json.loads(response.body.decode("utf-8"))
    return str(data["value"])

self.stored_value = gl.eq_principle.strict_eq(fetch)
```
Use when: data is stable (doesn't change between validators)

### Pattern 2: Fetch + Compare with Tolerance
```python
result = gl.eq_principle.prompt_comparative(
    fetch,
    principle="Values must be within 2% of each other."
)
```
Use when: data changes rapidly (prices, live counts)

### Pattern 3: Fetch + AI Reasoning
```python
def fetch_and_analyze() -> str:
    data = gl.nondet.web.get(url).body.decode("utf-8")
    prompt = f"Analyze this data: {data}. Return JSON."
    return gl.nondet.exec_prompt(prompt)

result = gl.eq_principle.prompt_comparative(
    fetch_and_analyze,
    principle="Key decisions must match."
)
```
Use when: data needs AI interpretation (sentiment, classification)

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| FINALIZED + ERROR | Wrong syntax or API blocked | Check error detail, try different API |
| Validators disagree | Data changed between calls | Use `prompt_comparative` instead of `strict_eq` |
| `read_*` shows empty/0 | Write not called yet | Call write function first, wait for SUCCESS |
| `read_*` shows old data | Reading from wrong state | Set State dropdown to **Finalized** |
| Timeout error | Too many API calls in one transaction | Split into smaller functions |

---

## Built For
GenLayer Tools & Infrastructure Bounty Task
**Repo:** https://github.com/Afghanistan8/genlayer-crypto-price-feed
