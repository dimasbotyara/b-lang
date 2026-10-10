"""Модуль файл/file."""
import os

MODULE_NAMES = ["файл", "file"]

def _read(a):
    with open(a[0], "r", encoding="utf-8") as f:
        return f.read()

def _write(a):
    with open(a[0], "w", encoding="utf-8") as f:
        f.write(str(a[1]))
    return True

def _append(a):
    with open(a[0], "a", encoding="utf-8") as f:
        f.write(str(a[1]))
    return True

FUNCTIONS = {
    "читать":   {"aliases": ["read"],   "handler": _read},
    "писать":   {"aliases": ["write"],  "handler": _write},
    "добавить": {"aliases": ["append"], "handler": _append},
    "есть":     {"aliases": ["exists"], "handler": lambda a: os.path.exists(a[0])},
    "удалить":  {"aliases": ["delete"], "handler": lambda a: os.remove(a[0]) or True},
    "список":   {"aliases": ["list"],   "handler": lambda a: os.listdir(a[0])},
}
