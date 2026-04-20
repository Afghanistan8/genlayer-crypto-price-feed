# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json
import typing


class HackerNewsSentiment(gl.Contract):
    # Single topic sentiment
    last_topic: str
    last_sentiment: str
    last_summary: str
    last_post_count: str

    # Top stories sentiment
    top_stories_sentiment: str
    top_stories_summary: str

    def __init__(self):
        self.last_topic = ""
        self.last_sentiment = ""
        self.last_summary = ""
        self.last_post_count = "0"
        self.top_stories_sentiment = ""
        self.top_stories_summary = ""

    @gl.public.write
    def analyze_topic(self, topic: str) -> typing.Any:
        # Use Algolia HN search API - free, no key needed
        search_url = f"https://hn.algolia.com/api/v1/search?query={topic}&tags=story&hitsPerPage=10"

        def fetch_and_analyze() -> str:
            # Fetch stories about the topic
            response = gl.nondet.web.get(search_url)
            data = json.loads(response.body.decode("utf-8"))

            # Extract titles and points from results
            stories = []
            for hit in data.get("hits", []):
                title = hit.get("title", "")
                points = hit.get("points", 0)
                comments = hit.get("num_comments", 0)
                if title:
                    stories.append(f"- {title} (points: {points}, comments: {comments})")

            if not stories:
                return json.dumps({
                    "sentiment": "Neutral",
                    "summary": "No stories found for this topic",
                    "post_count": "0"
                })

            stories_text = "\n".join(stories[:10])
            post_count = str(len(stories))

            # Use GenLayer's LLM to analyze sentiment
            prompt = f"""
            Analyze the sentiment of these Hacker News stories about "{topic}":

            {stories_text}

            Based on the titles and engagement (points and comments), determine:
            1. Overall sentiment: Positive, Negative, or Neutral
            2. A brief one-sentence summary of what the community thinks

            Respond ONLY with a valid JSON object in this exact format:
            {{"sentiment": "Positive", "summary": "brief summary here", "post_count": "{post_count}"}}

            Rules:
            - sentiment must be exactly one of: Positive, Negative, Neutral
            - summary must be one sentence only
            - post_count must be the number provided
            """

            result = gl.nondet.exec_prompt(prompt)
            # Clean up response and parse JSON
            clean = result.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return clean.strip()

        result = gl.eq_principle.prompt_comparative(
            fetch_and_analyze,
            principle="The sentiment classification must be the same (Positive/Negative/Neutral). The summary must convey the same meaning even if worded differently."
        )

        parsed = json.loads(result)
        self.last_topic = topic
        self.last_sentiment = parsed.get("sentiment", "Neutral")
        self.last_summary = parsed.get("summary", "")
        self.last_post_count = parsed.get("post_count", "0")

    @gl.public.write
    def analyze_top_stories(self) -> typing.Any:
        # Fetch top 10 story IDs from HN
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"

        def fetch_and_analyze() -> str:
            # Get top story IDs
            response = gl.nondet.web.get(top_url)
            ids = json.loads(response.body.decode("utf-8"))[:10]

            # Fetch each story title
            titles = []
            for story_id in ids:
                item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                item_response = gl.nondet.web.get(item_url)
                item = json.loads(item_response.body.decode("utf-8"))
                title = item.get("title", "")
                score = item.get("score", 0)
                if title:
                    titles.append(f"- {title} (score: {score})")

            stories_text = "\n".join(titles)

            # Use LLM to analyze overall sentiment of tech community
            prompt = f"""
            Analyze the overall sentiment and mood of the tech community 
            based on these current top Hacker News stories:

            {stories_text}

            Determine:
            1. Overall sentiment: Positive, Negative, or Neutral
            2. A brief one-sentence summary of what topics are trending

            Respond ONLY with a valid JSON object in this exact format:
            {{"sentiment": "Positive", "summary": "brief summary here"}}

            Rules:
            - sentiment must be exactly one of: Positive, Negative, Neutral
            - summary must be one sentence only
            """

            result = gl.nondet.exec_prompt(prompt)
            clean = result.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return clean.strip()

        result = gl.eq_principle.prompt_comparative(
            fetch_and_analyze,
            principle="The sentiment classification must be the same (Positive/Negative/Neutral). The summary must convey the same general meaning."
        )

        parsed = json.loads(result)
        self.top_stories_sentiment = parsed.get("sentiment", "Neutral")
        self.top_stories_summary = parsed.get("summary", "")

    @gl.public.view
    def read_topic_sentiment(self) -> dict:
        return {
            "topic": self.last_topic,
            "sentiment": self.last_sentiment,
            "summary": self.last_summary,
            "posts_analyzed": self.last_post_count
        }

    @gl.public.view
    def read_top_stories_sentiment(self) -> dict:
        return {
            "sentiment": self.top_stories_sentiment,
            "summary": self.top_stories_summary
        }
