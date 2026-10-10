"""Загрузчик модулей stdlib — автоматически подхватывает всё из папки."""
import importlib
import pkgutil
from pathlib import Path

_cache = {}
_registry = None

def _discover():
    """Сканирует папку stdlib/ и собирает все модули."""
    global _registry
    _registry = {}
    pkg_path = Path(__file__).parent
    for item in pkg_path.glob("std_*.py"):
        mod_name = item.stem  # std_random
        try:
            m = importlib.import_module(f"stdlib.{mod_name}")
            names = getattr(m, "MODULE_NAMES", [mod_name.replace("std_", "")])
            funcs = getattr(m, "FUNCTIONS", {})
            flat = {}
            for fname, info in funcs.items():
                handler = info["handler"]
                flat[fname] = handler
                for alias in info.get("aliases", []):
                    flat[alias] = handler
            for n in names:
                _registry[n] = {
                    "functions": flat,
                    "aliases": [a for a in names if a != n],
                    "names": [],
                }
        except Exception as e:
            print(f"⚠ Ошибка загрузки {mod_name}: {e}")

def load_module(name):
    global _registry
    if _registry is None:
        _discover()
    return _registry.get(name)

def all_modules():
    global _registry
    if _registry is None:
        _discover()
    return list(_registry.keys())
