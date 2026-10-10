# stdlib/std_rich.py
"""Модуль богатый/rich."""
MODULE_NAMES = ["богатый", "rich"]

def _print(a):
    try:
        from rich.console import Console
        c = Console()
        c.print(a[0], style=a[1] if len(a) > 1 else None)
    except ImportError:
        print(a[0])

def _panel(a):
    try:
        from rich.console import Console
        from rich.panel import Panel
        Console().print(Panel(str(a[0]), title=str(a[1]) if len(a) > 1 else None))
    except ImportError:
        print(f"=== {a[1] if len(a)>1 else ''} ===\n{a[0]}\n===")

def _rule(a):
    try:
        from rich.console import Console
        from rich.rule import Rule
        Console().print(Rule(str(a[0]) if a else ""))
    except ImportError:
        print("-" * 40)

def _tree(a):
    try:
        from rich.console import Console
        from rich.tree import Tree
        Console().print(Tree(str(a[0])))
    except ImportError:
        print(a[0])

def _code(a):
    try:
        from rich.console import Console
        from rich.syntax import Syntax
        Console().print(Syntax(str(a[0]), a[1] if len(a) > 1 else "python"))
    except ImportError:
        print(a[0])

FUNCTIONS = {
    "печать":  {"aliases": ["print"],  "handler": _print},
    "панель":  {"aliases": ["panel"],  "handler": _panel},
    "правило": {"aliases": ["rule"],   "handler": _rule},
    "дерево":  {"aliases": ["tree"],   "handler": _tree},
    "код":     {"aliases": ["code"],   "handler": _code},
}
