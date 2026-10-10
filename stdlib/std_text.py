"""Модуль текст/text."""
MODULE_NAMES = ["текст", "text"]

FUNCTIONS = {
    "длина":     {"aliases": ["len"],     "handler": lambda a: len(a[0])},
    "верх":      {"aliases": ["upper"],   "handler": lambda a: str(a[0]).upper()},
    "низ":       {"aliases": ["lower"],   "handler": lambda a: str(a[0]).lower()},
    "обрезать":  {"aliases": ["trim", "strip"], "handler": lambda a: str(a[0]).strip()},
    "заменить":  {"aliases": ["replace"], "handler": lambda a: str(a[0]).replace(a[1], a[2])},
    "найти":     {"aliases": ["find"],    "handler": lambda a: str(a[0]).find(a[1])},
    "разбить":   {"aliases": ["split"],   "handler": lambda a: str(a[0]).split(a[1]) if len(a) > 1 else str(a[0]).split()},
    "соединить": {"aliases": ["join"],    "handler": lambda a: a[1].join(str(x) for x in a[0])},
}
