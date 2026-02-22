import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from application.interfaces.fetcher import Fetcher

class HttpFetcher(Fetcher):
    """Получает HTML страницы по URL через HTTP с ретраями."""

    def __init__(self):
        self.session = requests.Session()
        retries = Retry(
            total=3,  # 3 попытки
            backoff_factor=2,  # экспоненциальная пауза между попытками
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch(self, url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        }

        # используем session, чтобы применялись ретраи
        response = self.session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text