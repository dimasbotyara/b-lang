"""Модуль сеть/net."""
import socket

MODULE_NAMES = ["сеть", "net"]

def _request(a):
    try:
        import requests
        return requests.get(a[0]).text
    except ImportError:
        return "⚠ Установите: pip install requests"

def _download(a):
    try:
        import requests
        r = requests.get(a[0])
        with open(a[1], "wb") as f:
            f.write(r.content)
        return True
    except ImportError:
        return "⚠ Установите: pip install requests"

def _ip(a):
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        return str(e)

FUNCTIONS = {
    "запрос":   {"aliases": ["request", "get"], "handler": _request},
    "скачать":  {"aliases": ["download"],       "handler": _download},
    "ip":       {"aliases": [],                 "handler": _ip},
}
