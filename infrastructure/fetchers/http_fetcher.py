import requests

from application.interfaces.fetcher import Fetcher


class HttpFetcher(Fetcher):
    """Получает HTML страницы по URL через HTTP."""
    
    def fetch(self, url: str) -> str:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
