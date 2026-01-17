"""
Web Search Tool for Council AI

Provides web search capabilities that can be used by LLMs during consultations.
Supports multiple search providers (Tavily, Serper, Google Custom Search, etc.)
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A single search result."""

    title: str
    url: str
    snippet: str
    content: Optional[str] = None  # Full content if available


@dataclass
class SearchResponse:
    """Response from a web search."""

    query: str
    results: List[SearchResult]
    total_results: int = 0


class WebSearchProvider(ABC):
    """Abstract base class for web search providers."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> SearchResponse:
        """Perform a web search.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            SearchResponse with results
        """
        pass


class TavilySearchProvider(WebSearchProvider):
    """Tavily AI search provider (https://tavily.com)."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Tavily provider.

        Args:
            api_key: Tavily API key (or from TAVILY_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Tavily API key required. Set TAVILY_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.base_url = "https://api.tavily.com"

    async def search(self, query: str, max_results: int = 5) -> SearchResponse:
        """Search using Tavily."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": True,
                    "include_raw_content": False,
                },
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("results", []):
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                    )
                )

            return SearchResponse(
                query=query,
                results=results,
                total_results=len(results),
            )


class SerperSearchProvider(WebSearchProvider):
    """Serper.dev search provider (https://serper.dev)."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Serper provider.

        Args:
            api_key: Serper API key (or from SERPER_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Serper API key required. Set SERPER_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.base_url = "https://google.serper.dev"

    async def search(self, query: str, max_results: int = 5) -> SearchResponse:
        """Search using Serper."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/search",
                headers={"X-API-KEY": self.api_key},
                json={"q": query, "num": max_results},
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("organic", []):
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                    )
                )

            return SearchResponse(
                query=query,
                results=results,
                total_results=data.get("searchInformation", {}).get("totalResults", 0),
            )


class GoogleCustomSearchProvider(WebSearchProvider):
    """Google Custom Search API provider."""

    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None):
        """Initialize Google Custom Search provider.

        Args:
            api_key: Google API key (or from GOOGLE_API_KEY env var)
            search_engine_id: Custom Search Engine ID (or from GOOGLE_CSE_ID env var)
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.search_engine_id = search_engine_id or os.environ.get("GOOGLE_CSE_ID")

        if not self.api_key:
            raise ValueError("Google API key required. Set GOOGLE_API_KEY environment variable.")
        if not self.search_engine_id:
            raise ValueError(
                "Google Custom Search Engine ID required. Set GOOGLE_CSE_ID environment variable."
            )

        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def search(self, query: str, max_results: int = 5) -> SearchResponse:
        """Search using Google Custom Search."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                self.base_url,
                params={
                    "key": self.api_key,
                    "cx": self.search_engine_id,
                    "q": query,
                    "num": min(max_results, 10),  # Google limits to 10
                },
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("items", []):
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                    )
                )

            return SearchResponse(
                query=query,
                results=results,
                total_results=int(data.get("searchInformation", {}).get("totalResults", 0)),
            )


class WebSearchTool:
    """Web search tool that can be used by LLMs."""

    def __init__(self, provider: Optional[WebSearchProvider] = None):
        """Initialize web search tool.

        Args:
            provider: Web search provider (auto-detects from env vars if None)
        """
        self.provider = provider or self._auto_detect_provider()

    def _auto_detect_provider(self) -> WebSearchProvider:
        """Auto-detect provider from environment variables."""
        if os.environ.get("TAVILY_API_KEY"):
            return TavilySearchProvider()
        elif os.environ.get("SERPER_API_KEY"):
            return SerperSearchProvider()
        elif os.environ.get("GOOGLE_API_KEY") and os.environ.get("GOOGLE_CSE_ID"):
            return GoogleCustomSearchProvider()
        else:
            raise ValueError(
                "No web search provider configured. Set one of: "
                "TAVILY_API_KEY, SERPER_API_KEY, or GOOGLE_API_KEY + GOOGLE_CSE_ID"
            )

    async def search(self, query: str, max_results: int = 5) -> SearchResponse:
        """Perform a web search."""
        return await self.provider.search(query, max_results)

    def format_search_results(self, response: SearchResponse) -> str:
        """Format search results as text for LLM context."""
        lines = [f"Web Search Results for: {response.query}", ""]

        for i, result in enumerate(response.results, 1):
            lines.append(f"{i}. {result.title}")
            lines.append(f"   URL: {result.url}")
            lines.append(f"   {result.snippet}")
            lines.append("")

        return "\n".join(lines)

    def get_function_definition(self) -> dict:
        """Get function definition for LLM function calling."""
        return {
            "name": "web_search",
            "description": (
                "Search the web for current information, facts, news, or research. "
                "Use this when you need up-to-date information "
                "that may not be in your training data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find information on the web",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-10)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": ["query"],
            },
        }
