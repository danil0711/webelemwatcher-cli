import requests

from application.interfaces.fetcher import Fetcher


class HttpFetcher(Fetcher):
    """Получает HTML страницы по URL через HTTP."""
    
    def fetch(self, url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
