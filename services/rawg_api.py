import logging
import os

import httpx
from cachetools import TTLCache

logger = logging.getLogger("bigcousin.rawg")


class RAWGClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.rawg.io/api"
        self._client = httpx.AsyncClient(timeout=8.0)
        self._search_cache = TTLCache(maxsize=200, ttl=3600)

    async def _request(self, endpoint: str, params: dict | None = None) -> dict:
        if params is None:
            params = {}
        params["key"] = self.api_key

        url = f"{self.base_url}/{endpoint}"
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def search(self, query: str, page_size: int = 5) -> list[dict]:
        cache_key = query.lower().strip()
        if cache_key in self._search_cache:
            logger.debug(f"Cache hit for search: {query}")
            return self._search_cache[cache_key]

        logger.info(f"Searching RAWG: {query}")
        data = await self._request("games", {
            "search": query,
            "page_size": page_size,
            "search_precise": False,
        })

        results = data.get("results", [])
        self._search_cache[cache_key] = results
        return results

    async def get_game_details(self, game_id: int) -> dict | None:
        cache_key = f"game_{game_id}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]

        try:
            data = await self._request(f"games/{game_id}")
            self._search_cache[cache_key] = data
            return data
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def _parse_game_data(self, raw: dict) -> dict:
        genres = [g["name"] for g in raw.get("genres", [])] if raw.get("genres") else None
        platforms = []
        if raw.get("platforms"):
            for p in raw["platforms"]:
                platform = p.get("platform")
                if platform:
                    platforms.append(platform["name"])

        release_year = None
        if raw.get("released"):
            release_year = int(raw["released"][:4])

        return {
            "id": raw["id"],
            "name": raw["name"],
            "cover_url": raw.get("background_image"),
            "description": raw.get("description_raw"),
            "genres": genres,
            "platforms": platforms if platforms else None,
            "release_year": release_year,
            "community_rating": raw.get("metacritic"),
        }

    async def search_and_parse(self, query: str) -> list[dict]:
        results = await self.search(query)
        return [self._parse_game_data(g) for g in results]

    async def get_game_details_parsed(self, game_id: int) -> dict | None:
        data = await self.get_game_details(game_id)
        if data is None:
            return None
        return self._parse_game_data(data)

    async def close(self):
        await self._client.aclose()


api_key = os.getenv("RAWG_API_KEY", "")
rawg_client = RAWGClient(api_key)
