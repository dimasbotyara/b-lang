"""Модуль время/time."""
import time
from datetime import datetime

MODULE_NAMES = ["время", "time"]

FUNCTIONS = {
    "сейчас":  {"aliases": ["now"],   "handler": lambda a: time.time()},
    "пауза":   {"aliases": ["sleep", "ждать", "wait"], "handler": lambda a: time.sleep(float(a[0]))},
    "дата":    {"aliases": ["date"],  "handler": lambda a: datetime.now().isoformat()},
    "год":     {"aliases": ["year"],  "handler": lambda a: datetime.now().year},
    "месяц":   {"aliases": ["month"], "handler": lambda a: datetime.now().month},
    "день":    {"aliases": ["day"],   "handler": lambda a: datetime.now().day},
    "час":     {"aliases": ["hour"],  "handler": lambda a: datetime.now().hour},
    "минута":  {"aliases": ["minute"],"handler": lambda a: datetime.now().minute},
    "секунда": {"aliases": ["second"],"handler": lambda a: datetime.now().second},
}
