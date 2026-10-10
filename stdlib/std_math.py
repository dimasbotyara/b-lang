"""Модуль математика/math."""
import math

MODULE_NAMES = ["математика", "math"]

FUNCTIONS = {
    "корень":       {"aliases": ["sqrt"],  "handler": lambda a: math.sqrt(a[0])},
    "степень":      {"aliases": ["pow"],   "handler": lambda a: math.pow(a[0], a[1])},
    "модуль":       {"aliases": ["abs"],   "handler": lambda a: abs(a[0])},
    "синус":        {"aliases": ["sin"],   "handler": lambda a: math.sin(a[0])},
    "косинус":      {"aliases": ["cos"],   "handler": lambda a: math.cos(a[0])},
    "тангенс":      {"aliases": ["tan"],   "handler": lambda a: math.tan(a[0])},
    "логарифм":     {"aliases": ["log"],   "handler": lambda a: math.log(a[0])},
    "логарифм10":   {"aliases": ["log10"], "handler": lambda a: math.log10(a[0])},
    "округлить":    {"aliases": ["round"], "handler": lambda a: round(a[0], int(a[1]) if len(a) > 1 else 0)},
    "вниз":         {"aliases": ["floor"], "handler": lambda a: math.floor(a[0])},
    "вверх":        {"aliases": ["ceil"],  "handler": lambda a: math.ceil(a[0])},
    "пи":           {"aliases": ["pi"],    "handler": lambda a: math.pi},
    "e":            {"aliases": [],        "handler": lambda a: math.e},
}
