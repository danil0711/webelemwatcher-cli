import queue
import threading

class EventBus:
    _instance = None
    _lock = threading.Lock()
    # Делаем возможным создание только одного экземпляра
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.queue = queue.Queue()
            return cls._instance

    def emit(self, message: str):
        """Добавить сообщение в очередь"""
        self.queue.put(message)

    def flush(self):
        """Достать все сообщения из очереди и вернуть списком"""
        messages = []
        while not self.queue.empty():
            messages.append(self.queue.get())
        return messages