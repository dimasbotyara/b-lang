# motivations/__init__.py
import random
from .ru import MOTIVATIONS_RU
from .en import MOTIVATIONS_EN

def get_motivation(lang="ru"):
    if lang == "en":
        return random.choice(MOTIVATIONS_EN)
    return random.choice(MOTIVATIONS_RU)

def detect_lang(code):
    """Определить доминирующий язык по коду."""
    ru = sum(1 for ch in code if 'а' <= ch.lower() <= 'я' or ch.lower() == 'ё')
    en = sum(1 for ch in code if 'a' <= ch.lower() <= 'z')
    return "ru" if ru >= en else "en"
