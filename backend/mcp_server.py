import requests
from typing import List, Dict

class MCPTools:
    """MCP Tools - Lightweight search wrapper"""

    def __init__(self):
        self.search_api_key = None  

    def search(self, query: str) -> List[Dict]:
        try:
            url = "https://api.duckduckgo.com/"
            params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
            response = requests.get(url, params=params, timeout=5)
            data = response.json()

            results = []

            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", "Result"),
                    "snippet": data.get("Abstract", ""),
                    "url": data.get("AbstractURL", "")
                })

            for topic in data.get("RelatedTopics", [])[:3]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": topic.get("Text")[:50],
                        "snippet": topic.get("Text"),
                        "url": topic.get("FirstURL", "")
                    })

            if not results:
                results.append({
                    "title": f"No direct search results for {query}",
                    "snippet": f"No relevant search results found. Relying on LLM to provide an accurate answer.",
                    "url": ""
                })

            return results

        except Exception as e:
            return [{
                "title": "Search Error",
                "snippet": f"Could not complete search: {str(e)}",
                "url": ""
            }]

    def fetch_content(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=5)
            return response.text[:1000]
        except Exception as e:
            return f"Error fetching content: {str(e)}"

    def summarize(self, text: str) -> str:
        sentences = text.split(". ")
        return ". ".join(sentences[:3]) + "." if sentences else text
