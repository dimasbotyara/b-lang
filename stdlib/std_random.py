"""Модуль рандом/random."""
import random

MODULE_NAMES = ["рандом", "random"]

def _number(args):
    a, b = int(args[0]), int(args[1])
    return random.randint(a, b)

def _float(args):
    return random.random()

def _choice(args):
    lst = args[0]
    if len(args) > 1:
        return random.sample(lst, int(args[1]))
    return random.choice(lst)

def _shuffle(args):
    lst = list(args[0])
    random.shuffle(lst)
    return lst

def _sample(args):
    return random.sample(args[0], int(args[1]))

def _coin(args): return random.choice([0, 1])
def _dice(args): return random.randint(1, 6)
def _seed(args):
    random.seed(args[0])
    return None

FUNCTIONS = {
    "число":      {"aliases": ["number"],   "handler": _number},
    "дробь":      {"aliases": ["float"],    "handler": _float},
    "выбор":      {"aliases": ["choice"],   "handler": _choice},
    "перемешать": {"aliases": ["shuffle"],  "handler": _shuffle},
    "образец":    {"aliases": ["sample"],   "handler": _sample},
    "монетка":    {"aliases": ["coin"],     "handler": _coin},
    "кубик":      {"aliases": ["dice"],     "handler": _dice},
    "зерно":      {"aliases": ["seed"],     "handler": _seed},
}
