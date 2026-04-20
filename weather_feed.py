# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json
import typing


# Weather condition codes from Open-Meteo WMO standard
def get_condition_description(code: int) -> str:
    conditions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Icy fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight showers",
        81: "Moderate showers",
        82: "Violent showers",
        95: "Thunderstorm",
        99: "Thunderstorm with hail",
    }
    return conditions.get(code, "Unknown")


class WeatherFeed(gl.Contract):
    # Single city storage
    last_city: str
    last_condition: str
    last_humidity: str

    # Multi city storage
    lagos_condition: str
    lagos_humidity: str
    london_condition: str
    london_humidity: str
    newyork_condition: str
    newyork_humidity: str
    tokyo_condition: str
    tokyo_humidity: str
    dubai_condition: str
    dubai_humidity: str

    def __init__(self):
        self.last_city = ""
        self.last_condition = ""
        self.last_humidity = ""
        self.lagos_condition = ""
        self.lagos_humidity = ""
        self.london_condition = ""
        self.london_humidity = ""
        self.newyork_condition = ""
        self.newyork_humidity = ""
        self.tokyo_condition = ""
        self.tokyo_humidity = ""
        self.dubai_condition = ""
        self.dubai_humidity = ""

    @gl.public.write
    def get_weather(self, city: str, latitude: str, longitude: str) -> typing.Any:
        api_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            f"&current=weather_code,relative_humidity_2m"
        )

        def fetch() -> str:
            response = gl.nondet.web.get(api_url)
            data = json.loads(response.body.decode("utf-8"))
            code = int(data["current"]["weather_code"])
            humidity = str(data["current"]["relative_humidity_2m"])
            condition = get_condition_description(code)
            return json.dumps({
                "condition": condition,
                "humidity": humidity
            }, sort_keys=True)

        result = gl.eq_principle.prompt_comparative(
            fetch,
            principle="The weather condition must be the same. Humidity must be within 5% of each other."
        )

        parsed = json.loads(result)
        self.last_city = city
        self.last_condition = parsed["condition"]
        self.last_humidity = parsed["humidity"]

    @gl.public.write
    def get_cities_weather(self) -> typing.Any:
        # Coordinates: Lagos, London, New York, Tokyo, Dubai
        cities = {
            "lagos":   ("6.5244", "3.3792"),
            "london":  ("51.5074", "-0.1278"),
            "newyork": ("40.7128", "-74.0060"),
            "tokyo":   ("35.6762", "139.6503"),
            "dubai":   ("25.2048", "55.2708"),
        }

        def fetch_all() -> str:
            results = {}
            for city, (lat, lon) in cities.items():
                url = (
                    f"https://api.open-meteo.com/v1/forecast"
                    f"?latitude={lat}&longitude={lon}"
                    f"&current=weather_code,relative_humidity_2m"
                )
                response = gl.nondet.web.get(url)
                data = json.loads(response.body.decode("utf-8"))
                code = int(data["current"]["weather_code"])
                humidity = str(data["current"]["relative_humidity_2m"])
                condition = get_condition_description(code)
                results[city] = {
                    "condition": condition,
                    "humidity": humidity
                }
            return json.dumps(results, sort_keys=True)

        result = gl.eq_principle.prompt_comparative(
            fetch_all,
            principle="Weather conditions must be the same for each city. Humidity values must be within 5% of each other."
        )

        parsed = json.loads(result)
        self.lagos_condition = parsed["lagos"]["condition"]
        self.lagos_humidity = parsed["lagos"]["humidity"]
        self.london_condition = parsed["london"]["condition"]
        self.london_humidity = parsed["london"]["humidity"]
        self.newyork_condition = parsed["newyork"]["condition"]
        self.newyork_humidity = parsed["newyork"]["humidity"]
        self.tokyo_condition = parsed["tokyo"]["condition"]
        self.tokyo_humidity = parsed["tokyo"]["humidity"]
        self.dubai_condition = parsed["dubai"]["condition"]
        self.dubai_humidity = parsed["dubai"]["humidity"]

    @gl.public.view
    def read_weather(self) -> dict:
        return {
            "city": self.last_city,
            "condition": self.last_condition,
            "humidity_%": self.last_humidity
        }

    @gl.public.view
    def read_cities_weather(self) -> dict:
        return {
            "Lagos":    {"condition": self.lagos_condition,   "humidity_%": self.lagos_humidity},
            "London":   {"condition": self.london_condition,  "humidity_%": self.london_humidity},
            "New York": {"condition": self.newyork_condition, "humidity_%": self.newyork_humidity},
            "Tokyo":    {"condition": self.tokyo_condition,   "humidity_%": self.tokyo_humidity},
            "Dubai":    {"condition": self.dubai_condition,   "humidity_%": self.dubai_humidity},
        }
