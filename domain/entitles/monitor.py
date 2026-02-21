class Monitor:
    """
    Описывает источник данных и способ извлечения значения.
    """

    def __init__(self, monitor_id: str, url: str, selector: str):
        self.id = monitor_id
        self.url = url
        self.selector = selector  # CSS селектор для извлечения значения

    def __repr__(self):
        return f"Monitor(id='{self.id}', url='{self.url}', selector='{self.selector}')"
