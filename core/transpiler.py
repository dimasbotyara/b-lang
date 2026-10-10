"""
Транспайлер b → чистый Python.
Превращает AST языка b в читаемый, самодостаточный Python-код.
"""
from pathlib import Path
from core.lexer import tokenize
from core.parser import *
from core.keywords import normalize_type


class TranspileError(Exception):
    pass


# ===== Таблицы имён =====

# Модули b → Python импорты
MODULE_IMPORTS = {
    "рандом": "random", "random": "random",
    "математика": "math", "math": "math",
    "время": "time", "time": "time",
    "файл": "os", "file": "os",
    "текст": None, "text": None,  # методы строк
    "сеть": "requests", "net": "requests",
    "система": "sys", "sys": "sys",
    "криптография": "hashlib", "crypto": "hashlib",
    "богатый": "rich", "rich": "rich",
    "вопрос": "questionary", "ask": "questionary",
}

# Маппинг функций модулей на Python-эквиваленты
# {модуль_b: {функция_b: (python_код, нужные_импорты)}}
MODULE_FUNC_MAP = {
    "рандом": {
        "число":      ("random.randint({0}, {1})", ["random"]),
        "number":     ("random.randint({0}, {1})", ["random"]),
        "дробь":      ("random.random()", ["random"]),
        "float":      ("random.random()", ["random"]),
        "выбор":      ("random.choice({0})", ["random"]),
        "choice":     ("random.choice({0})", ["random"]),
        "перемешать": ("__b_shuffle({0})", ["random"]),
        "shuffle":    ("__b_shuffle({0})", ["random"]),
        "образец":    ("random.sample({0}, {1})", ["random"]),
        "sample":     ("random.sample({0}, {1})", ["random"]),
        "монетка":    ("random.choice([0, 1])", ["random"]),
        "coin":       ("random.choice([0, 1])", ["random"]),
        "кубик":      ("random.randint(1, 6)", ["random"]),
        "dice":       ("random.randint(1, 6)", ["random"]),
        "зерно":      ("random.seed({0})", ["random"]),
        "seed":       ("random.seed({0})", ["random"]),
    },
    "random": {  # алиас
        "number":  ("random.randint({0}, {1})", ["random"]),
        "float":   ("random.random()", ["random"]),
        "choice":  ("random.choice({0})", ["random"]),
        "shuffle": ("__b_shuffle({0})", ["random"]),
        "sample":  ("random.sample({0}, {1})", ["random"]),
        "coin":    ("random.choice([0, 1])", ["random"]),
        "dice":    ("random.randint(1, 6)", ["random"]),
        "seed":    ("random.seed({0})", ["random"]),
    },
    "математика": {
        "корень":     ("math.sqrt({0})", ["math"]),
        "sqrt":       ("math.sqrt({0})", ["math"]),
        "степень":    ("math.pow({0}, {1})", ["math"]),
        "pow":        ("math.pow({0}, {1})", ["math"]),
        "модуль":     ("abs({0})", []),
        "abs":        ("abs({0})", []),
        "синус":      ("math.sin({0})", ["math"]),
        "sin":        ("math.sin({0})", ["math"]),
        "косинус":    ("math.cos({0})", ["math"]),
        "cos":        ("math.cos({0})", ["math"]),
        "тангенс":    ("math.tan({0})", ["math"]),
        "tan":        ("math.tan({0})", ["math"]),
        "логарифм":   ("math.log({0})", ["math"]),
        "log":        ("math.log({0})", ["math"]),
        "логарифм10": ("math.log10({0})", ["math"]),
        "log10":      ("math.log10({0})", ["math"]),
        "округлить":  ("round({0})", []),
        "round":      ("round({0})", []),
        "вниз":       ("math.floor({0})", ["math"]),
        "floor":      ("math.floor({0})", ["math"]),
        "вверх":      ("math.ceil({0})", ["math"]),
        "ceil":       ("math.ceil({0})", ["math"]),
        "пи":         ("math.pi", ["math"]),
        "pi":         ("math.pi", ["math"]),
        "e":          ("math.e", ["math"]),
    },
    "math": {
        "sqrt":  ("math.sqrt({0})", ["math"]),
        "pow":   ("math.pow({0}, {1})", ["math"]),
        "abs":   ("abs({0})", []),
        "sin":   ("math.sin({0})", ["math"]),
        "cos":   ("math.cos({0})", ["math"]),
        "tan":   ("math.tan({0})", ["math"]),
        "log":   ("math.log({0})", ["math"]),
        "log10": ("math.log10({0})", ["math"]),
        "round": ("round({0})", []),
        "floor": ("math.floor({0})", ["math"]),
        "ceil":  ("math.ceil({0})", ["math"]),
        "pi":    ("math.pi", ["math"]),
        "e":     ("math.e", ["math"]),
    },
    "время": {
        "сейчас":  ("time.time()", ["time"]),
        "now":     ("time.time()", ["time"]),
        "пауза":   ("time.sleep({0})", ["time"]),
        "sleep":   ("time.sleep({0})", ["time"]),
        "ждать":   ("time.sleep({0})", ["time"]),
        "дата":    ("datetime.datetime.now().isoformat()", ["datetime"]),
        "date":    ("datetime.datetime.now().isoformat()", ["datetime"]),
        "год":     ("datetime.datetime.now().year", ["datetime"]),
        "year":    ("datetime.datetime.now().year", ["datetime"]),
        "месяц":   ("datetime.datetime.now().month", ["datetime"]),
        "month":   ("datetime.datetime.now().month", ["datetime"]),
        "день":    ("datetime.datetime.now().day", ["datetime"]),
        "day":     ("datetime.datetime.now().day", ["datetime"]),
        "час":     ("datetime.datetime.now().hour", ["datetime"]),
        "hour":    ("datetime.datetime.now().hour", ["datetime"]),
        "минута":  ("datetime.datetime.now().minute", ["datetime"]),
        "minute":  ("datetime.datetime.now().minute", ["datetime"]),
        "секунда": ("datetime.datetime.now().second", ["datetime"]),
        "second":  ("datetime.datetime.now().second", ["datetime"]),
    },
    "time": {
        "now":    ("time.time()", ["time"]),
        "sleep":  ("time.sleep({0})", ["time"]),
        "date":   ("datetime.datetime.now().isoformat()", ["datetime"]),
        "year":   ("datetime.datetime.now().year", ["datetime"]),
        "month":  ("datetime.datetime.now().month", ["datetime"]),
        "day":    ("datetime.datetime.now().day", ["datetime"]),
        "hour":   ("datetime.datetime.now().hour", ["datetime"]),
        "minute": ("datetime.datetime.now().minute", ["datetime"]),
        "second": ("datetime.datetime.now().second", ["datetime"]),
    },
    "файл": {
        "читать":   ("__b_file_read({0})", []),
        "read":     ("__b_file_read({0})", []),
        "писать":   ("__b_file_write({0}, {1})", []),
        "write":    ("__b_file_write({0}, {1})", []),
        "добавить": ("__b_file_append({0}, {1})", []),
        "append":   ("__b_file_append({0}, {1})", []),
        "есть":     ("os.path.exists({0})", ["os"]),
        "exists":   ("os.path.exists({0})", ["os"]),
        "удалить":  ("os.remove({0})", ["os"]),
        "delete":   ("os.remove({0})", ["os"]),
        "список":   ("os.listdir({0})", ["os"]),
        "list":     ("os.listdir({0})", ["os"]),
    },
    "file": {
        "read":   ("__b_file_read({0})", []),
        "write":  ("__b_file_write({0}, {1})", []),
        "append": ("__b_file_append({0}, {1})", []),
        "exists": ("os.path.exists({0})", ["os"]),
        "delete": ("os.remove({0})", ["os"]),
        "list":   ("os.listdir({0})", ["os"]),
    },
    "текст": {
        "длина":     ("len({0})", []),
        "len":       ("len({0})", []),
        "верх":      ("str({0}).upper()", []),
        "upper":     ("str({0}).upper()", []),
        "низ":       ("str({0}).lower()", []),
        "lower":     ("str({0}).lower()", []),
        "обрезать":  ("str({0}).strip()", []),
        "trim":      ("str({0}).strip()", []),
        "strip":     ("str({0}).strip()", []),
        "заменить":  ("str({0}).replace({1}, {2})", []),
        "replace":   ("str({0}).replace({1}, {2})", []),
        "найти":     ("str({0}).find({1})", []),
        "find":      ("str({0}).find({1})", []),
        "разбить":   ("str({0}).split({1})", []),
        "split":     ("str({0}).split({1})", []),
        "соединить": ("{1}.join(str(x) for x in {0})", []),
        "join":      ("{1}.join(str(x) for x in {0})", []),
    },
    "text": {
        "len":     ("len({0})", []),
        "upper":   ("str({0}).upper()", []),
        "lower":   ("str({0}).lower()", []),
        "trim":    ("str({0}).strip()", []),
        "strip":   ("str({0}).strip()", []),
        "replace": ("str({0}).replace({1}, {2})", []),
        "find":    ("str({0}).find({1})", []),
        "split":   ("str({0}).split({1})", []),
        "join":    ("{1}.join(str(x) for x in {0})", []),
    },
    "сеть": {
        "запрос":  ("requests.get({0}).text", ["requests"]),
        "request": ("requests.get({0}).text", ["requests"]),
        "get":     ("requests.get({0}).text", ["requests"]),
        "скачать": ("__b_download({0}, {1})", ["requests"]),
        "download":("__b_download({0}, {1})", ["requests"]),
        "ip":      ("socket.gethostbyname(socket.gethostname())", ["socket"]),
    },
    "net": {
        "request": ("requests.get({0}).text", ["requests"]),
        "download":("__b_download({0}, {1})", ["requests"]),
        "ip":      ("socket.gethostbyname(socket.gethostname())", ["socket"]),
    },
    "система": {
        "аргументы": ("sys.argv[1:]", ["sys"]),
        "args":      ("sys.argv[1:]", ["sys"]),
        "выход":     ("sys.exit({0})", ["sys"]),
        "exit":      ("sys.exit({0})", ["sys"]),
        "имя_ос":    ("os.name", ["os"]),
        "os_name":   ("os.name", ["os"]),
        "запустить": ("os.system({0})", ["os"]),
        "run":       ("os.system({0})", ["os"]),
        "переменная":("os.environ.get({0}, '')", ["os"]),
        "env":       ("os.environ.get({0}, '')", ["os"]),
    },
    "sys": {
        "args":    ("sys.argv[1:]", ["sys"]),
        "exit":    ("sys.exit({0})", ["sys"]),
        "os_name": ("os.name", ["os"]),
        "run":     ("os.system({0})", ["os"]),
        "env":     ("os.environ.get({0}, '')", ["os"]),
    },
    "криптография": {
        "md5":    ("hashlib.md5(str({0}).encode()).hexdigest()", ["hashlib"]),
        "sha1":   ("hashlib.sha1(str({0}).encode()).hexdigest()", ["hashlib"]),
        "sha256": ("hashlib.sha256(str({0}).encode()).hexdigest()", ["hashlib"]),
        "sha512": ("hashlib.sha512(str({0}).encode()).hexdigest()", ["hashlib"]),
        "blake2": ("hashlib.blake2b(str({0}).encode()).hexdigest()", ["hashlib"]),
        "sha3":   ("hashlib.sha3_256(str({0}).encode()).hexdigest()", ["hashlib"]),
        "токен":  ("secrets.token_hex({0})", ["secrets"]),
        "token":  ("secrets.token_hex({0})", ["secrets"]),
        "соль":   ("secrets.token_bytes({0}).hex()", ["secrets"]),
        "salt":   ("secrets.token_bytes({0}).hex()", ["secrets"]),
        "ключ":   ("secrets.token_bytes({0}).hex()", ["secrets"]),
        "key":    ("secrets.token_bytes({0}).hex()", ["secrets"]),
        "uuid":   ("str(uuid.uuid4())", ["uuid"]),
        "base64": ("base64.b64encode(str({0}).encode()).decode()", ["base64"]),
        "base64_декод":  ("base64.b64decode({0}).decode()", ["base64"]),
        "base64_decode": ("base64.b64decode({0}).decode()", ["base64"]),
        "hex":           ("str({0}).encode().hex()", []),
        "hex_декод":     ("bytes.fromhex({0}).decode()", []),
        "hex_decode":    ("bytes.fromhex({0}).decode()", []),
        "url_код":       ("urllib.parse.quote(str({0}))", ["urllib.parse"]),
        "url_encode":    ("urllib.parse.quote(str({0}))", ["urllib.parse"]),
    },
    "crypto": {
        "md5":    ("hashlib.md5(str({0}).encode()).hexdigest()", ["hashlib"]),
        "sha1":   ("hashlib.sha1(str({0}).encode()).hexdigest()", ["hashlib"]),
        "sha256": ("hashlib.sha256(str({0}).encode()).hexdigest()", ["hashlib"]),
        "sha512": ("hashlib.sha512(str({0}).encode()).hexdigest()", ["hashlib"]),
        "blake2": ("hashlib.blake2b(str({0}).encode()).hexdigest()", ["hashlib"]),
        "sha3":   ("hashlib.sha3_256(str({0}).encode()).hexdigest()", ["hashlib"]),
        "token":  ("secrets.token_hex({0})", ["secrets"]),
        "salt":   ("secrets.token_bytes({0}).hex()", ["secrets"]),
        "key":    ("secrets.token_bytes({0}).hex()", ["secrets"]),
        "uuid":   ("str(uuid.uuid4())", ["uuid"]),
        "base64": ("base64.b64encode(str({0}).encode()).decode()", ["base64"]),
        "base64_decode": ("base64.b64decode({0}).decode()", ["base64"]),
        "hex":           ("str({0}).encode().hex()", []),
        "hex_decode":    ("bytes.fromhex({0}).decode()", []),
        "url_encode":    ("urllib.parse.quote(str({0}))", ["urllib.parse"]),
    },
}

# Специальные "модули" объекты (например, цвет)
SPECIAL_OBJECTS = {
    "цвет": {
        "радуга":   ("__b_rainbow({0})", []),
        "rainbow":  ("__b_rainbow({0})", []),
        "огонь":    ("__b_fire({0})", []),
        "fire":     ("__b_fire({0})", []),
        "градиент": ("__b_gradient({0}, {1}, {2})", []),
        "gradient": ("__b_gradient({0}, {1}, {2})", []),
        "микс":     ("__b_mix({0}, {1})", []),
        "mix":      ("__b_mix({0}, {1})", []),
        "палитра":  ("__b_show_palette()", []),
        "palette":  ("__b_show_palette()", []),
    },
    "color": {
        "rainbow":  ("__b_rainbow({0})", []),
        "fire":     ("__b_fire({0})", []),
        "gradient": ("__b_gradient({0}, {1}, {2})", []),
        "mix":      ("__b_mix({0}, {1})", []),
        "palette":  ("__b_show_palette()", []),
    },
}

# Методы строк/списков (для obj.method)
STRING_METHODS = {
    "длина": "len({obj})", "len": "len({obj})",
    "верх": "{obj}.upper()", "upper": "{obj}.upper()",
    "низ": "{obj}.lower()", "lower": "{obj}.lower()",
    "обрезать": "{obj}.strip()", "trim": "{obj}.strip()", "strip": "{obj}.strip()",
    "разбить": "{obj}.split({args})", "split": "{obj}.split({args})",
    "заменить": "{obj}.replace({args})", "replace": "{obj}.replace({args})",
    "найти": "{obj}.find({args})", "find": "{obj}.find({args})",
}

LIST_METHODS = {
    "длина": "len({obj})", "len": "len({obj})",
    "добавить": "{obj}.append({args})", "push": "{obj}.append({args})", "append": "{obj}.append({args})",
    "убрать": "{obj}.pop({args})", "pop": "{obj}.pop({args})",
    "сортировать": "sorted({obj})", "sort": "sorted({obj})",
}


# ===== Транспайлер =====

class Transpiler:
    """Превращает AST b в чистый Python-код."""

    def __init__(self):
        self.indent_level = 0
        self.imports = set()           # обычные импорты
        self.module_aliases = {}       # {b_имя: модуль} — какие модули импортированы в b-коде
        self.helpers_needed = set()    # имена helper-функций, которые нужно включить
        self.var_types = {}            # {имя: тип} — для проверок/приведений
        self.in_function = False
        self.in_class = False
        self.use_rich = False          # использовать rich для цветной печати

    # ---------- вспомогательные ----------
    def indent(self):
        return "    " * self.indent_level

    def _py_name(self, name):
        """Безопасное имя для Python (кириллица допустима в Python 3)."""
        # Избегаем конфликтов с ключевыми словами Python
        PY_KEYWORDS = {"class", "def", "if", "else", "elif", "while", "for",
                       "return", "import", "from", "as", "try", "except",
                       "finally", "raise", "pass", "break", "continue",
                       "and", "or", "not", "in", "is", "lambda", "with",
                       "yield", "global", "nonlocal", "True", "False", "None"}
        if name in PY_KEYWORDS:
            return name + "_"
        return name

    def _escape_str(self, s):
        """Экранирует строку для Python-литерала."""
        return repr(s)

    # ---------- вход ----------
    def transpile(self, program):
        # Сначала собираем тело
        body_lines = []
        for stmt in program.body:
            lines = self.gen_stmt(stmt)
            body_lines.extend(lines)

        # Собираем шапку
        header = self._gen_header()
        helpers = self._gen_helpers()

        result = header
        if helpers:
            result += "\n" + helpers + "\n"
        result += "\n# ===== Программа =====\n"
        result += "\n".join(body_lines)
        if not result.endswith("\n"):
            result += "\n"
        return result

    def _gen_header(self):
        lines = [
            "#!/usr/bin/env python3",
            '"""Автоматически сгенерировано транспайлером b → Python."""',
            "",
        ]

        # Импорты — всегда нужные
        std_imports = sorted(self.imports)
        for imp in std_imports:
            if imp == "urllib.parse":
                lines.append("import urllib.parse")
            else:
                lines.append(f"import {imp}")

        if self.use_rich:
            lines.append("try:")
            lines.append("    from rich.console import Console")
            lines.append("    from rich.text import Text")
            lines.append("    _b_console = Console()")
            lines.append("    _B_HAS_RICH = True")
            lines.append("except ImportError:")
            lines.append("    _B_HAS_RICH = False")

        lines.append("")
        return "\n".join(lines)

    def _gen_helpers(self):
        """Генерирует встроенные helper-функции."""
        helpers = []

        if "__b_print" in self.helpers_needed:
            helpers.append(HELPER_PRINT)
        if "__b_input_to_num" in self.helpers_needed:
            helpers.append(HELPER_INPUT_NUM)
        if "__b_coerce" in self.helpers_needed:
            helpers.append(HELPER_COERCE)
        if "__b_file_read" in self.helpers_needed:
            helpers.append(HELPER_FILE)
        if "__b_shuffle" in self.helpers_needed:
            helpers.append(HELPER_SHUFFLE)
        if "__b_rainbow" in self.helpers_needed:
            helpers.append(HELPER_COLOR_FUNCS)
        if "__b_download" in self.helpers_needed:
            helpers.append(HELPER_DOWNLOAD)
        if "__b_fstring" in self.helpers_needed:
            helpers.append(HELPER_FSTRING)
        if "__b_warn" in self.helpers_needed:
            helpers.append(HELPER_WARN)

        return "\n\n".join(helpers)

    # ---------- операторы ----------
    def gen_stmt(self, stmt):
        method = getattr(self, f"gen_{type(stmt).__name__}", None)
        if not method:
            raise TranspileError(f"Нет генератора для {type(stmt).__name__}")
        result = method(stmt)
        if isinstance(result, str):
            return [self.indent() + result]
        return result

    def gen_Let(self, node):
        name = self._py_name(node.name)
        self.var_types[node.name] = node.type

        if node.value is None:
            return [self.indent() + f"{name} = None"]

        value = self.gen_expr(node.value)

        # Приведение типа при объявлении
        if node.type and node.type != "any":
            self.helpers_needed.add("__b_coerce")
            value = f"__b_coerce({value}, {self._escape_str(node.type)})"

        return [self.indent() + f"{name} = {value}"]

    def gen_Assign(self, node):
        value = self.gen_expr(node.value)
        target = self.gen_lvalue(node.target)

        # Если известен тип переменной — приведём
        if isinstance(node.target, Name):
            t = self.var_types.get(node.target.name)
            if t and t != "any":
                self.helpers_needed.add("__b_coerce")
                value = f"__b_coerce({value}, {self._escape_str(t)})"

        return [self.indent() + f"{target} = {value}"]

    def gen_lvalue(self, node):
        """Генерирует Python-выражение для присваивания слева."""
        if isinstance(node, Name):
            return self._py_name(node.name)
        if isinstance(node, Index):
            obj = self.gen_expr(node.obj)
            idx = self.gen_expr(node.idx)
            return f"{obj}[{idx}]"
        if isinstance(node, Attr):
            obj = self.gen_expr(node.obj)
            return f"{obj}.{self._py_name(node.attr)}"
        raise TranspileError(f"Невозможно присвоить {type(node).__name__}")

    def gen_Print(self, node):
        """Генерирует вызов print с цветами через rich (если есть)."""
        parts = [self.gen_expr(a) for a in node.args]

        has_style = node.fg or node.bg or node.styles

        if has_style:
            self.use_rich = True
            self.helpers_needed.add("__b_print")
            fg = self._escape_str(node.fg) if node.fg else "None"
            bg = self._escape_str(node.bg) if node.bg else "None"
            styles = "[" + ", ".join(self._escape_str(s) for s in node.styles) + "]"
            if not parts:
                return [self.indent() + f"__b_print('', fg={fg}, bg={bg}, styles={styles})"]
            if len(parts) == 1:
                return [self.indent() + f"__b_print({parts[0]}, fg={fg}, bg={bg}, styles={styles})"]
            return [self.indent() + f"__b_print(' '.join(str(x) for x in [{', '.join(parts)}]), fg={fg}, bg={bg}, styles={styles})"]

        # Обычный print
        if not parts:
            return [self.indent() + "print()"]
        if len(parts) == 1:
            return [self.indent() + f"print({parts[0]})"]
        return [self.indent() + f"print({', '.join(parts)})"]

    def gen_If(self, node):
        lines = []
        cond = self.gen_expr(node.cond)
        lines.append(self.indent() + f"if {cond}:")
        self.indent_level += 1
        for s in node.body:
            lines.extend(self.gen_stmt(s))
        self.indent_level -= 1

        for econd, ebody in node.elifs:
            c = self.gen_expr(econd)
            lines.append(self.indent() + f"elif {c}:")
            self.indent_level += 1
            for s in ebody:
                lines.extend(self.gen_stmt(s))
            self.indent_level -= 1

        if node.else_body:
            lines.append(self.indent() + "else:")
            self.indent_level += 1
            for s in node.else_body:
                lines.extend(self.gen_stmt(s))
            self.indent_level -= 1

        return lines

    def gen_While(self, node):
        lines = []
        cond = self.gen_expr(node.cond)
        lines.append(self.indent() + f"while {cond}:")
        self.indent_level += 1
        for s in node.body:
            lines.extend(self.gen_stmt(s))
        self.indent_level -= 1
        return lines

    def gen_For(self, node):
        lines = []
        var = self._py_name(node.var)

        if node.iterable is not None:
            it = self.gen_expr(node.iterable)
            lines.append(self.indent() + f"for {var} in {it}:")
        else:
            start = self.gen_expr(node.start)
            end = self.gen_expr(node.end)
            step = self.gen_expr(node.step) if node.step else "1"
            # По умолчанию включительно
            if not node.exclusive:
                # Нужно +1 к концу (или -1 если шаг отрицательный)
                # Для простоты оборачиваем в helper или используем условие на шаг
                if step == "1":
                    end_expr = f"({end}) + 1"
                else:
                    end_expr = f"({end}) + (1 if ({step}) > 0 else -1)"
            else:
                end_expr = end
            lines.append(self.indent() + f"for {var} in range(int({start}), int({end_expr}), int({step})):")

        self.indent_level += 1
        for s in node.body:
            lines.extend(self.gen_stmt(s))
        self.indent_level -= 1
        return lines

    def gen_FunctionDef(self, node):
        lines = []
        name = self._py_name(node.name)
        params = []
        for pname, ptype in node.params:
            params.append(self._py_name(pname))

        lines.append(self.indent() + f"def {name}({', '.join(params)}):")
        self.indent_level += 1

        # Приведение типов параметров
        for pname, ptype in node.params:
            if ptype and ptype != "any":
                self.helpers_needed.add("__b_coerce")
                py = self._py_name(pname)
                lines.append(self.indent() + f"{py} = __b_coerce({py}, {self._escape_str(ptype)})")

        was_in_fn = self.in_function
        self.in_function = True
        saved_types = dict(self.var_types)

        if not node.body:
            lines.append(self.indent() + "pass")
        else:
            for s in node.body:
                lines.extend(self.gen_stmt(s))

        self.var_types = saved_types
        self.in_function = was_in_fn
        self.indent_level -= 1
        return lines

    def gen_ClassDef(self, node):
        lines = []
        name = self._py_name(node.name)
        lines.append(self.indent() + f"class {name}:")
        self.indent_level += 1

        # Собираем поля (Let) и методы (FunctionDef)
        attrs = [s for s in node.body if isinstance(s, Let)]
        methods = [s for s in node.body if isinstance(s, FunctionDef)]

        # __init__ если есть "инит" или "init"
        init_method = None
        for m in methods:
            if m.name in ("инит", "init"):
                init_method = m
                break

        if attrs or init_method:
            params = []
            if init_method:
                for pname, ptype in init_method.params:
                    params.append(self._py_name(pname))
            lines.append(self.indent() + f"def __init__(self, {', '.join(params)}):")
            self.indent_level += 1
            # Поля
            for a in attrs:
                val = self.gen_expr(a.value) if a.value else "None"
                lines.append(self.indent() + f"self.{self._py_name(a.name)} = {val}")
            # Код инита
            if init_method:
                was = self.in_class
                self.in_class = True
                # Подменим "я"/"self" на self внутри
                for s in init_method.body:
                    lines.extend(self._gen_method_body_stmt(s))
                if not init_method.body:
                    lines.append(self.indent() + "pass")
                self.in_class = was
            elif not attrs:
                lines.append(self.indent() + "pass")
            self.indent_level -= 1

        # Остальные методы
        other_methods = [m for m in methods if m.name not in ("инит", "init")]
        for m in other_methods:
            mname = self._py_name(m.name)
            params = ["self"] + [self._py_name(p) for p, _ in m.params]
            lines.append(self.indent() + f"def {mname}({', '.join(params)}):")
            self.indent_level += 1
            was = self.in_class
            self.in_class = True
            if not m.body:
                lines.append(self.indent() + "pass")
            else:
                for s in m.body:
                    lines.extend(self._gen_method_body_stmt(s))
            self.in_class = was
            self.indent_level -= 1

        if not attrs and not methods:
            lines.append(self.indent() + "pass")

        self.indent_level -= 1
        return lines

    def _gen_method_body_stmt(self, stmt):
        """То же, что gen_stmt, но заменяет 'я'/'self'/'this' на Python self."""
        # Наш gen_expr уже умеет через _py_name — но нужно обрабатывать имя 'я' → 'self'
        return self.gen_stmt(stmt)

    def gen_Return(self, node):
        if node.value is None:
            return [self.indent() + "return"]
        return [self.indent() + f"return {self.gen_expr(node.value)}"]

    def gen_Import(self, node):
        """Запоминаем — какой модуль импортирован."""
        name = node.name
        self.module_aliases[name] = name
        # Автоматически подключаем Python-импорт
        py_mod = MODULE_IMPORTS.get(name)
        if py_mod:
            self.imports.add(py_mod)
        # Доп. импорты, которые часто нужны
        if name in ("время", "time"):
            self.imports.add("datetime")
        if name in ("криптография", "crypto"):
            # на всякий случай добавим часто нужные
            self.imports.add("hashlib")
        return []  # сам import не генерирует код — импорты в шапке

    def gen_Try(self, node):
        lines = [self.indent() + "try:"]
        self.indent_level += 1
        if not node.body:
            lines.append(self.indent() + "pass")
        for s in node.body:
            lines.extend(self.gen_stmt(s))
        self.indent_level -= 1

        if node.catch_body is not None:
            if node.catch_var:
                lines.append(self.indent() + f"except Exception as _b_e:")
                self.indent_level += 1
                lines.append(self.indent() + f"{self._py_name(node.catch_var)} = str(_b_e)")
            else:
                lines.append(self.indent() + "except Exception:")
                self.indent_level += 1
            if not node.catch_body:
                lines.append(self.indent() + "pass")
            for s in node.catch_body:
                lines.extend(self.gen_stmt(s))
            self.indent_level -= 1

        if node.finally_body is not None:
            lines.append(self.indent() + "finally:")
            self.indent_level += 1
            if not node.finally_body:
                lines.append(self.indent() + "pass")
            for s in node.finally_body:
                lines.extend(self.gen_stmt(s))
            self.indent_level -= 1

        return lines

    def gen_Throw(self, node):
        v = self.gen_expr(node.value)
        return [self.indent() + f"raise Exception(str({v}))"]

    def gen_WarnNode(self, node):
        self.helpers_needed.add("__b_warn")
        v = self.gen_expr(node.value)
        return [self.indent() + f"__b_warn({v})"]

    def gen_Pass(self, node):
        return [self.indent() + "pass"]

    def gen_Break(self, node):
        return [self.indent() + "break"]

    def gen_Continue(self, node):
        return [self.indent() + "continue"]

    def gen_ExprStmt(self, node):
        return [self.indent() + self.gen_expr(node.expr)]

    # ---------- выражения ----------
    def gen_expr(self, node):
        method = getattr(self, f"ge_{type(node).__name__}", None)
        if not method:
            raise TranspileError(f"Нет генератора выражения для {type(node).__name__}")
        return method(node)

    def ge_Num(self, n):
        return str(n.value)

    def ge_Str(self, n):
        if n.has_interp:
            # Парсим выражения внутри {выражение} b-языка и транслируем их в Python
            import re
            s = n.value
            def repl(m):
                expr = m.group(1).strip()
                try:
                    tokens = tokenize(expr)
                    filtered = [t for t in tokens if t.type not in (TokType.INDENT, TokType.NEWLINE)]
                    ast = Parser(filtered)
                    expr_node = ast.parse_expr()
                    # Транспилируем внутреннее выражение в чистый Python!
                    py_expr = self.gen_expr(expr_node)
                    return "{" + py_expr + "}"
                except Exception:
                    return "{" + expr + "}"

            transpiled_str = re.sub(r"\{([^{}]+)\}", repl, s)
            return "f" + self._escape_str(transpiled_str)
        return self._escape_str(n.value)

    def ge_Bool(self, n):
        return "True" if n.value else "False"

    def ge_Null(self, n):
        return "None"

    def ge_Name(self, n):
        # Специальные имена
        if n.name.lower() in ("я", "self", "this"):
            if self.in_class:
                return "self"
        return self._py_name(n.name)

    def ge_ListLit(self, n):
        items = [self.gen_expr(i) for i in n.items]
        return "[" + ", ".join(items) + "]"

    def ge_DictLit(self, n):
        pairs = [f"{self.gen_expr(k)}: {self.gen_expr(v)}" for k, v in n.pairs]
        return "{" + ", ".join(pairs) + "}"

    def ge_BinOp(self, n):
        l = self.gen_expr(n.left)
        r = self.gen_expr(n.right)
        op = n.op

        if op == "and":
            return f"({l} and {r})"
        if op == "or":
            return f"({l} or {r})"
        if op == "+":
            # Для совместимости со строками используем helper на уровне b (там предупреждение)
            # В Python просто +. str+str и num+num работают, а смешанные упадут.
            # Можно обернуть в helper, но пусть по-простому:
            return f"({l} + {r})"
        if op in ("-", "*", "/", "%"):
            if op == "/":
                # Нужна защита от деления на ноль — Python сам кинет ZeroDivisionError
                return f"({l} / {r})"
            return f"({l} {op} {r})"
        if op in ("==", "!=", "<", ">", "<=", ">="):
            return f"({l} {op} {r})"
        raise TranspileError(f"Неизвестная бинарная операция: {op}")

    def ge_UnaryOp(self, n):
        v = self.gen_expr(n.operand)
        if n.op == "-":
            return f"(-{v})"
        if n.op == "not":
            return f"(not {v})"
        return v

    def ge_Attr(self, n):
        # Проверка: может это модуль?
        if isinstance(n.obj, Name):
            mod_name = n.obj.name
            # Специальные (цвет)
            if mod_name in SPECIAL_OBJECTS:
                # Привет: это обращение, но без вызова — вернём "частичное" выражение
                # В случае обращения без вызова просто сошлёмся на helper без аргументов
                # Но правильнее — такие вещи почти всегда вызываются через Call
                attr = n.attr.lower()
                if attr in SPECIAL_OBJECTS[mod_name]:
                    # Возвращаем "недовызванное" — помечаем как плейсхолдер
                    # Чтобы работало без () — пропишем lambda
                    tpl, _ = SPECIAL_OBJECTS[mod_name][attr]
                    # Если нет аргументов — просто вызовем
                    if "{0}" not in tpl:
                        self.helpers_needed.update(self._helper_names_for_special(mod_name, attr))
                        return tpl
                    # Иначе — вернём "функцию", которую смогут вызвать далее
                    self.helpers_needed.update(self._helper_names_for_special(mod_name, attr))
                    # Генерируем lambda, принимающую сколько надо аргументов (хак — через *args)
                    return self._make_lambda_for(tpl)

            if mod_name in self.module_aliases and mod_name in MODULE_FUNC_MAP:
                attr = n.attr.lower()
                func_map = MODULE_FUNC_MAP[mod_name]
                if attr in func_map:
                    tpl, imps = func_map[attr]
                    for i in imps:
                        self.imports.add(i)
                    if "{0}" not in tpl:
                        # без аргументов
                        return tpl
                    return self._make_lambda_for(tpl)

        obj = self.gen_expr(n.obj)
        return f"{obj}.{self._py_name(n.attr)}"

    def _helper_names_for_special(self, mod, attr):
        """Добавить нужные helper-функции для специального объекта."""
        names = set()
        if mod in ("цвет", "color"):
            if attr in ("радуга", "rainbow"): names.add("__b_rainbow")
            if attr in ("огонь", "fire"): names.add("__b_rainbow")  # общий файл
            if attr in ("градиент", "gradient"): names.add("__b_rainbow")
            if attr in ("микс", "mix"): names.add("__b_rainbow")
            if attr in ("палитра", "palette"): names.add("__b_rainbow")
        return names

    def _make_lambda_for(self, tpl):
        """Делает lambda, которую можно вызвать с нужными аргументами."""
        # Количество плейсхолдеров
        import re
        placeholders = sorted(set(int(m.group(1)) for m in re.finditer(r"\{(\d+)\}", tpl)))
        n = len(placeholders)
        if n == 0:
            return f"(lambda: {tpl})"
        args = ", ".join(f"_a{i}" for i in range(n))
        body = tpl
        for i in range(n):
            body = body.replace("{" + str(i) + "}", f"_a{i}")
        return f"(lambda {args}: {body})"

    def ge_Index(self, n):
        obj = self.gen_expr(n.obj)
        idx = self.gen_expr(n.idx)
        return f"{obj}[{idx}]"

    def ge_Call(self, n):
        # Специальный случай: вызов модуль.функция ARGS
        if isinstance(n.func, Attr) and isinstance(n.func.obj, Name):
            mod = n.func.obj.name
            attr = n.func.attr.lower()

            # Спец-объекты (цвет.радуга и т.д.)
            if mod in SPECIAL_OBJECTS and attr in SPECIAL_OBJECTS[mod]:
                tpl, _ = SPECIAL_OBJECTS[mod][attr]
                self.helpers_needed.update(self._helper_names_for_special(mod, attr))
                return self._format_tpl(tpl, n.args)

            # Импортированные модули
            if mod in self.module_aliases and mod in MODULE_FUNC_MAP:
                func_map = MODULE_FUNC_MAP[mod]
                if attr in func_map:
                    tpl, imps = func_map[attr]
                    for i in imps:
                        self.imports.add(i)
                    # Регистрируем нужные helper-функции
                    self._register_helpers_for_tpl(tpl)
                    return self._format_tpl(tpl, n.args)

            # Методы строк/списков — делаем через getattr или просто
            # (не можем знать тип статически; оставим как obj.method(args))

        # Обычный вызов
        func = self.gen_expr(n.func)
        args = ", ".join(self.gen_expr(a) for a in n.args)
        return f"{func}({args})"

    def _register_helpers_for_tpl(self, tpl):
        """Если в шаблоне есть __b_XXX — зарегистрировать как нужный."""
        import re
        for m in re.finditer(r"__b_\w+", tpl):
            self.helpers_needed.add(m.group(0))

    def _format_tpl(self, tpl, args_nodes):
        """Подставляет аргументы в шаблон вида 'func({0}, {1})'."""
        args = [self.gen_expr(a) for a in args_nodes]
        # Поддерживаем {0}, {1}, ...
        import re
        def repl(m):
            idx = int(m.group(1))
            if idx < len(args):
                return args[idx]
            return "None"
        result = re.sub(r"\{(\d+)\}", repl, tpl)
        return result

    def ge_InputExpr(self, n):
        prompt = self.gen_expr(n.prompt) if n.prompt else "''"
        default = self.gen_expr(n.default) if n.default else "None"

        if n.strict:
            # Строгий режим — просто input (приведение упадёт, если неверный)
            return f"input(str({prompt}))"

        # С дефолтом или без
        if n.default is not None:
            self.helpers_needed.add("__b_input_to_num")
            return f"__b_input_with_default(input(str({prompt})), {default})"

        return f"input(str({prompt}))"


# ===== Helper-функции (включаются в сгенерированный код) =====

HELPER_PRINT = '''\
def __b_print(text, fg=None, bg=None, styles=None):
    """Цветная печать с поддержкой rich и ANSI-fallback."""
    _palette = {
        "красный":"#FF0000","red":"#FF0000","зелёный":"#00FF00","зеленый":"#00FF00",
        "green":"#00FF00","синий":"#0000FF","blue":"#0000FF","жёлтый":"#FFFF00",
        "желтый":"#FFFF00","yellow":"#FFFF00","голубой":"#00FFFF","cyan":"#00FFFF",
        "белый":"#FFFFFF","white":"#FFFFFF","чёрный":"#000000","черный":"#000000",
        "black":"#000000","розовый":"#FFC0CB","pink":"#FFC0CB","пурпурный":"#800080",
        "purple":"#800080","лиловый":"#EE82EE","violet":"#EE82EE","бирюзовый":"#40E0D0",
        "turquoise":"#40E0D0","изумрудный":"#50C878","emerald":"#50C878","лаймовый":"#CCFF00",
        "lime":"#CCFF00","оливковый":"#808000","olive":"#808000","бежевый":"#F5F5DC",
        "beige":"#F5F5DC","коричневый":"#8B4513","brown":"#8B4513","серый":"#808080",
        "gray":"#808080","оранжевый":"#FFA500","orange":"#FFA500","коралловый":"#FF7F50",
        "coral":"#FF7F50","мандарин":"#FF8243","mandarin":"#FF8243","янтарь":"#FFBF00",
        "янтарный":"#FFBF00","amber":"#FFBF00","золотой":"#FFD700","gold":"#FFD700",
    }
    _style_map = {
        "жирный":"bold","bold":"bold","тусклый":"dim","dim":"dim",
        "курсив":"italic","italic":"italic","подчёркнутый":"underline",
        "подчеркнутый":"underline","underline":"underline","мигающий":"blink",
        "blink":"blink","инверсный":"reverse","reverse":"reverse",
        "зачёркнутый":"strike","зачеркнутый":"strike","strikethrough":"strike",
    }
    def _resolve(c):
        if not c: return None
        c = str(c).strip()
        if c.startswith("#"): return c
        if c.startswith("rgb"):
            import re as _re
            nums = _re.findall(r"\\d+", c)
            if len(nums) >= 3:
                return "#{:02X}{:02X}{:02X}".format(int(nums[0]), int(nums[1]), int(nums[2]))
        return _palette.get(c.lower())

    if _B_HAS_RICH:
        parts = []
        if styles:
            for s in styles:
                m = _style_map.get(s.lower() if isinstance(s, str) else s)
                if m: parts.append(m)
        c = _resolve(fg)
        if c: parts.append(c)
        c = _resolve(bg)
        if c: parts.append("on " + c)
        style = " ".join(parts) if parts else None
        if style:
            _b_console.print(text, style=style)
        else:
            _b_console.print(text)
        return

    # ANSI fallback
    codes = []
    style_codes = {"bold":"1","dim":"2","italic":"3","underline":"4",
                   "blink":"5","reverse":"7","strike":"9"}
    if styles:
        for s in styles:
            m = _style_map.get(s.lower() if isinstance(s, str) else s)
            if m and m in style_codes:
                codes.append(style_codes[m])
    c = _resolve(fg)
    if c:
        r, g, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        codes.append("38;2;{};{};{}".format(r, g, b))
    c = _resolve(bg)
    if c:
        r, g, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        codes.append("48;2;{};{};{}".format(r, g, b))
    if codes:
        print("\\033[" + ";".join(codes) + "m" + str(text) + "\\033[0m")
    else:
        print(text)
'''

HELPER_INPUT_NUM = '''\
def __b_input_with_default(raw, default):
    """Пробует привести ввод к числу, при неудаче — default."""
    try:
        s = str(raw).strip()
        if not s:
            return default
        if "." in s:
            return float(s)
        return int(s)
    except (ValueError, TypeError):
        return default
'''

HELPER_COERCE = '''\
def __b_coerce(value, type_):
    """Мягкое приведение типа с предупреждением при неудаче."""
    try:
        if type_ == "number":
            if isinstance(value, bool): return int(value)
            if isinstance(value, (int, float)): return value
            if isinstance(value, str):
                v = value.strip()
                if not v: return 0
                if "." in v: return float(v)
                return int(v)
            return 0
        if type_ == "string":
            return str(value) if value is not None else ""
        if type_ == "bool":
            if isinstance(value, str):
                return value.lower() not in ("", "ложь", "false", "0", "нет", "no")
            return bool(value)
        if type_ == "list":
            if isinstance(value, list): return value
            if value is None: return []
            try: return list(value)
            except: return [value]
        if type_ == "dict":
            if isinstance(value, dict): return value
            if value is None: return {}
            return dict(value)
        return value
    except Exception:
        import sys
        print("\\033[33m⚠ Не удалось привести к " + type_ + "\\033[0m", file=sys.stderr)
        return value
'''

HELPER_FILE = '''\
def __b_file_read(path):
    with open(path, "r", encoding="utf-8") as _f:
        return _f.read()

def __b_file_write(path, text):
    with open(path, "w", encoding="utf-8") as _f:
        _f.write(str(text))
    return True

def __b_file_append(path, text):
    with open(path, "a", encoding="utf-8") as _f:
        _f.write(str(text))
    return True
'''

HELPER_SHUFFLE = '''\
def __b_shuffle(lst):
    import random as _r
    lst = list(lst)
    _r.shuffle(lst)
    return lst
'''

HELPER_DOWNLOAD = '''\
def __b_download(url, path):
    import requests as _r
    resp = _r.get(url)
    with open(path, "wb") as _f:
        _f.write(resp.content)
    return True
'''

HELPER_COLOR_FUNCS = '''\
_B_PALETTE = {
    "красный":"#FF0000","red":"#FF0000","зелёный":"#00FF00","green":"#00FF00",
    "синий":"#0000FF","blue":"#0000FF","жёлтый":"#FFFF00","yellow":"#FFFF00",
    "розовый":"#FFC0CB","pink":"#FFC0CB","пурпурный":"#800080","purple":"#800080",
    "бирюзовый":"#40E0D0","turquoise":"#40E0D0","изумрудный":"#50C878","emerald":"#50C878",
    "оранжевый":"#FFA500","orange":"#FFA500","коралловый":"#FF7F50","coral":"#FF7F50",
    "янтарный":"#FFBF00","amber":"#FFBF00","золотой":"#FFD700","gold":"#FFD700",
    "фиолетовый":"#8000FF","magenta":"#FF00FF","белый":"#FFFFFF","white":"#FFFFFF",
}

def _b_resolve_color(c):
    if not c: return "#FFFFFF"
    c = str(c).strip()
    if c.startswith("#"): return c
    return _B_PALETTE.get(c.lower(), "#FFFFFF")

def __b_rainbow(text):
    colors = ["#FF0000","#FF8800","#FFFF00","#00FF00","#00FFFF","#0088FF","#8800FF"]
    s = str(text)
    try:
        from rich.console import Console as _C
        from rich.text import Text as _T
        t = _T()
        for i, ch in enumerate(s):
            t.append(ch, style=colors[i % len(colors)])
        _C().print(t)
    except ImportError:
        out = ""
        for i, ch in enumerate(s):
            hex_c = colors[i % len(colors)]
            r,g,b = int(hex_c[1:3],16), int(hex_c[3:5],16), int(hex_c[5:7],16)
            out += "\\033[38;2;{};{};{}m{}".format(r, g, b, ch)
        print(out + "\\033[0m")

def __b_fire(text):
    colors = ["#FFFF00","#FFAA00","#FF6600","#FF3300","#CC0000"]
    s = str(text)
    try:
        from rich.console import Console as _C
        from rich.text import Text as _T
        t = _T()
        for i, ch in enumerate(s):
            idx = int(i / max(1, len(s)-1) * (len(colors)-1))
            t.append(ch, style=colors[idx])
        _C().print(t)
    except ImportError:
        print(s)

def __b_gradient(text, c1, c2):
    c1 = _b_resolve_color(c1); c2 = _b_resolve_color(c2)
    r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    s = str(text)
    n = max(1, len(s)-1)
    try:
        from rich.console import Console as _C
        from rich.text import Text as _T
        t = _T()
        for i, ch in enumerate(s):
            r = int(r1 + (r2-r1)*i/n)
            g = int(g1 + (g2-g1)*i/n)
            b = int(b1 + (b2-b1)*i/n)
            t.append(ch, style="#{:02X}{:02X}{:02X}".format(r,g,b))
        _C().print(t)
    except ImportError:
        print(s)

def __b_mix(c1, c2):
    c1 = _b_resolve_color(c1); c2 = _b_resolve_color(c2)
    r = (int(c1[1:3],16) + int(c2[1:3],16)) // 2
    g = (int(c1[3:5],16) + int(c2[3:5],16)) // 2
    b = (int(c1[5:7],16) + int(c2[5:7],16)) // 2
    return "#{:02X}{:02X}{:02X}".format(r, g, b)

def __b_show_palette():
    try:
        from rich.console import Console as _C
        from rich.table import Table as _TB
        t = _TB(title="🎨 Палитра")
        t.add_column("Имя"); t.add_column("Hex"); t.add_column("Пример")
        seen = set()
        for name, hex_c in _B_PALETTE.items():
            if hex_c in seen: continue
            seen.add(hex_c)
            t.add_row(name, hex_c, "[{}]██████[/{}]".format(hex_c, hex_c))
        _C().print(t)
    except ImportError:
        for name, hex_c in _B_PALETTE.items():
            print("  " + name + ": " + hex_c)
'''

HELPER_FSTRING = '''\
# (не используется — f-строки Python покрывают интерполяцию {expr})
'''

HELPER_WARN = '''\
def __b_warn(message):
    """Выводит предупреждение янтарным цветом."""
    try:
        from rich.console import Console as _C
        _C().print("⚠ Предупреждение: " + str(message), style="#FFBF00 bold")
    except ImportError:
        print("\\033[38;2;255;191;0m⚠ Предупреждение: " + str(message) + "\\033[0m")
'''


# ===== API =====
def transpile_file(filename):
    """Транспилирует файл .b в Python-код (строка)."""
    src = Path(filename).read_text(encoding="utf-8")
    return transpile_source(src)

def transpile_source(src):
    """Транспилирует исходник .b (строка) в Python-код."""
    tokens = tokenize(src)
    ast = Parser(tokens).parse()
    return Transpiler().transpile(ast)

def transpile_to_file(input_path, output_path=None):
    """Транспилирует .b файл и сохраняет в .py."""
    code = transpile_file(input_path)
    if output_path is None:
        output_path = str(Path(input_path).with_suffix(".py"))
    Path(output_path).write_text(code, encoding="utf-8")
    return output_path
