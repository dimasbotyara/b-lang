"""Модуль система/sys."""
import sys
import os

MODULE_NAMES = ["система", "sys"]

FUNCTIONS = {
    "аргументы": {"aliases": ["args"],    "handler": lambda a: sys.argv[1:]},
    "выход":     {"aliases": ["exit"],    "handler": lambda a: sys.exit(int(a[0]) if a else 0)},
    "имя_ос":    {"aliases": ["os_name"], "handler": lambda a: os.name},
    "запустить": {"aliases": ["run"],     "handler": lambda a: os.system(a[0])},
    "переменная":{"aliases": ["env"],     "handler": lambda a: os.environ.get(a[0], "")},
}
