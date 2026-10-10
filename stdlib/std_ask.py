# stdlib/std_ask.py
"""Модуль вопрос/ask (questionary)."""
MODULE_NAMES = ["вопрос", "ask"]

def _text(a):
    try:
        import questionary
        return questionary.text(a[0]).ask()
    except ImportError:
        return input(a[0] + " ")

def _password(a):
    try:
        import questionary
        return questionary.password(a[0]).ask()
    except ImportError:
        import getpass
        return getpass.getpass(a[0] + " ")

def _confirm(a):
    try:
        import questionary
        return questionary.confirm(a[0]).ask()
    except ImportError:
        return input(a[0] + " (y/n): ").lower().startswith("y")

def _select(a):
    try:
        import questionary
        return questionary.select(a[0], choices=list(a[1])).ask()
    except ImportError:
        print(a[0])
        for i, c in enumerate(a[1]):
            print(f"  {i+1}. {c}")
        idx = int(input("> ")) - 1
        return a[1][idx]

def _checkbox(a):
    try:
        import questionary
        return questionary.checkbox(a[0], choices=list(a[1])).ask()
    except ImportError:
        return list(a[1])

def _path(a):
    try:
        import questionary
        return questionary.path(a[0]).ask()
    except ImportError:
        return input(a[0] + " ")

FUNCTIONS = {
    "текст":        {"aliases": ["text"],         "handler": _text},
    "пароль":       {"aliases": ["password"],     "handler": _password},
    "подтвердить":  {"aliases": ["confirm"],      "handler": _confirm},
    "выбор":        {"aliases": ["select"],       "handler": _select},
    "галочки":      {"aliases": ["checkbox"],     "handler": _checkbox},
    "путь":         {"aliases": ["path"],         "handler": _path},
}
