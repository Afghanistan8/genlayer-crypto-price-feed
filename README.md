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
