"""Tests for the Web Search tool providers and helper methods."""

import os
import pytest
import httpx
from types import SimpleNamespace

from council_ai.tools.web_search import (
    SearchResult,
    SearchResponse,
    TavilySearchProvider,
    SerperSearchProvider,
    GoogleCustomSearchProvider,
    WebSearchTool,
)


# Helper async client mocks
class DummyResponse:
    def __init__(self, json_data, status=200):
        self._json = json_data
        self.status_code = status

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=None)


class DummyAsyncClient:
    def __init__(self, *, json_data=None, method="post"):
        self._json_data = json_data or {}
        self._method = method

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        return DummyResponse(self._json_data)

    async def get(self, *args, **kwargs):
        return DummyResponse(self._json_data)


@pytest.mark.asyncio
async def test_tavily_search_success(monkeypatch):
    json_data = {"results": [{"title": "T1", "url": "http://t1", "content": "snippet"}]}
    monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: DummyAsyncClient(json_data=json_data))

    provider = TavilySearchProvider(api_key="test-key")
    resp = await provider.search("test query", max_results=2)

    assert isinstance(resp, SearchResponse)
    assert resp.total_results == 1
    assert resp.results[0].title == "T1"


@pytest.mark.asyncio
async def test_serper_search_success(monkeypatch):
    json_data = {"organic": [{"title": "S1", "link": "http://s1", "snippet": "s"}], "searchInformation": {"totalResults": "5"}}
    monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: DummyAsyncClient(json_data=json_data))

    provider = SerperSearchProvider(api_key="serper-key")
    resp = await provider.search("hello", max_results=3)

    assert resp.query == "hello"
    assert resp.total_results == "5" or resp.total_results == 5
    assert resp.results[0].title == "S1"


@pytest.mark.asyncio
async def test_google_custom_search_success(monkeypatch):
    json_data = {"items": [{"title": "G1", "link": "http://g1", "snippet": "g"}], "searchInformation": {"totalResults": "10"}}
    monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: DummyAsyncClient(json_data=json_data, method="get"))

    provider = GoogleCustomSearchProvider(api_key="gkey", search_engine_id="cx")
    resp = await provider.search("query", max_results=20)

    assert resp.total_results == 10
    assert len(resp.results) == 1
    assert resp.results[0].url == "http://g1"


def test_auto_detect_provider(monkeypatch):
    # Tavily preferred when env set
    monkeypatch.setenv("TAVILY_API_KEY", "x")
    tool = WebSearchTool()
    assert tool.provider.__class__.__name__ == "TavilySearchProvider"
    monkeypatch.delenv("TAVILY_API_KEY")

    # Serper
    monkeypatch.setenv("SERPER_API_KEY", "y")
    tool = WebSearchTool()
    assert tool.provider.__class__.__name__ == "SerperSearchProvider"
    monkeypatch.delenv("SERPER_API_KEY")

    # Google
    monkeypatch.setenv("GOOGLE_API_KEY", "gk")
    monkeypatch.setenv("GOOGLE_CSE_ID", "cx")
    tool = WebSearchTool()
    assert tool.provider.__class__.__name__ == "GoogleCustomSearchProvider"
    monkeypatch.delenv("GOOGLE_API_KEY")
    monkeypatch.delenv("GOOGLE_CSE_ID")


def test_format_search_results_and_function_def():
    results = [SearchResult(title="T1", url="u1", snippet="s1"), SearchResult(title="T2", url="u2", snippet="s2")]
    resp = SearchResponse(query="q", results=results, total_results=2)

    tool = WebSearchTool(provider=SimpleNamespace(search=lambda *a, **k: resp))
    formatted = tool.format_search_results(resp)
    assert "Web Search Results for: q" in formatted
    assert "1. T1" in formatted

    fdef = tool.get_function_definition()
    assert fdef["name"] == "web_search"
    assert "query" in fdef["parameters"]["properties"]
    assert fdef["parameters"]["properties"]["max_results"]["maximum"] == 10


@pytest.mark.asyncio
async def test_search_delegates_to_provider(monkeypatch):
    called = {"called": False}

    class FakeProvider:
        async def search(self, q, max_results=5):
            called["called"] = True
            return SearchResponse(query=q, results=[], total_results=0)

    tool = WebSearchTool(provider=FakeProvider())
    resp = await tool.search("qq", max_results=2)
    assert called["called"]
    assert resp.query == "qq"
