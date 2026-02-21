from bs4 import BeautifulSoup


class Extractor:
    """Извлекает значение из HTML по CSS селектору и нормализует его."""

    def __init__(self, value_type: str = "text"):
        """
        `value_type` - "text" или "numeric"
        """
        self.value_type = value_type

    def extract(self, html: str, selector: str):
        soup = BeautifulSoup(html, "html.parser")
        element = soup.select_one(selector)
        if not element:
            raise ValueError(f"Selector {selector} не нашёл элемент.")

        text = element.get_text(strip=True)

        if self.value_type == "numeric":
            numeric_value = self._extract_numeric(text)
            try:
                return float(numeric_value)
            except ValueError:
                raise ValueError(f"Не удалось преобразовать '{text}' в число")
        else:
            return text

    def _extract_numeric(self, text: str) -> str:
        """Оставляет только цифры и точку."""
        result = []
        for ch in text:
            if ch.isdigit() or ch == ".":
                result.append(ch)
        return "".join(result)

    def __repr__(self):
        return f"Extractor(value_type='{self.value_type}')"
