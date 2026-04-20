# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json
import typing


class CryptoPriceFeed(gl.Contract):
    last_price: str
    last_coin: str
    btc_price: str
    eth_price: str
    bnb_price: str
    sol_price: str
    xrp_price: str

    def __init__(self):
        self.last_price = "0"
        self.last_coin = ""
        self.btc_price = "0"
        self.eth_price = "0"
        self.bnb_price = "0"
        self.sol_price = "0"
        self.xrp_price = "0"

    @gl.public.write
    def get_price(self, symbol: str) -> typing.Any:
        api_url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"

        def fetch():
            response = gl.nondet.web.get(api_url)
            data = json.loads(response.body.decode("utf-8"))
            return str(data["price"])

        self.last_price = gl.eq_principle.strict_eq(fetch)
        self.last_coin = symbol

    @gl.public.write
    def get_top5_prices(self) -> typing.Any:

        def fetch_all():
            btc = json.loads(gl.nondet.web.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            ).body.decode("utf-8"))["price"]

            eth = json.loads(gl.nondet.web.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
            ).body.decode("utf-8"))["price"]

            bnb = json.loads(gl.nondet.web.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"
            ).body.decode("utf-8"))["price"]

            sol = json.loads(gl.nondet.web.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT"
            ).body.decode("utf-8"))["price"]

            xrp = json.loads(gl.nondet.web.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=XRPUSDT"
            ).body.decode("utf-8"))["price"]

            return json.dumps({
                "BTC": btc,
                "ETH": eth,
                "BNB": bnb,
                "SOL": sol,
                "XRP": xrp
            }, sort_keys=True)

        result = gl.eq_principle.prompt_comparative(
            fetch_all,
            principle="The crypto prices for each coin must be within 2% of each other. The coin names BTC, ETH, BNB, SOL, XRP must all be present and identical."
        )

        parsed = json.loads(result)
        self.btc_price = parsed["BTC"]
        self.eth_price = parsed["ETH"]
        self.bnb_price = parsed["BNB"]
        self.sol_price = parsed["SOL"]
        self.xrp_price = parsed["XRP"]

    @gl.public.view
    def read_price(self) -> dict:
        return {
            "coin": self.last_coin,
            "price_usd": self.last_price
        }

    @gl.public.view
    def read_all_prices(self) -> dict:
        return {
            "BTC": self.btc_price,
            "ETH": self.eth_price,
            "BNB": self.bnb_price,
            "SOL": self.sol_price,
            "XRP": self.xrp_price
        }
