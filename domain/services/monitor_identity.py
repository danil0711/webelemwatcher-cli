import hashlib


def generate_monitor_id(url: str, selector: str, value_type: str) -> str:
    raw = f"{url}|{selector}|{value_type}"
    return hashlib.sha256(raw.encode()).hexdigest()
