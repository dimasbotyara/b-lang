"""Интерпретатор b."""
import sys
import time
from pathlib import Path

from core.parser import *
from core.lexer import tokenize
from core.errors import (BError, BRuntimeError, BTypeError, BNameError,
                          BImportError, handle_warning)
from core.colors import cprint, resolve_color, rainbow, fire, gradient, mix, show_palette
from core.keywords import normalize_type
from motivations import detect_lang

# ===== Scope =====
class Scope:
    def __init__(self, parent=None):
        self.vars = {}
        self.types = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise BNameError(f"Переменная '{name}' не объявлена",
                        hint=f"Объяви её: пусть {name} = значение")

    def set(self, name, value, type_=None, declare=False):
        if declare:
            self.vars[name] = value
            if type_:
                self.types[name] = type_
            return
        # Присваивание уже существующей
        s = self
        while s:
            if name in s.vars:
                s.vars[name] = value
                return
            s = s.parent
        # Если нигде нет — создаём в текущем
        self.vars[name] = value

    def has(self, name):
        if name in self.vars: return True
        return self.parent.has(name) if self.parent else False

    def get_type(self, name):
        if name in self.types:
            return self.types[name]
        if self.parent:
            return self.parent.get_type(name)
        return None


# ===== Функции / классы =====
class BFunction:
    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure
    def __repr__(self):
        return f"<функция {self.name}>"

class BClass:
    def __init__(self, name, methods, attrs):
        self.name = name
        self.methods = methods
        self.attrs = attrs
    def __repr__(self):
        return f"<класс {self.name}>"

class BInstance:
    def __init__(self, cls):
        self.cls = cls
        self.fields = dict(cls.attrs)
    def __repr__(self):
        return f"<{self.cls.name}>"

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass


# ===== Интерпретатор =====
class Interpreter:
    def __init__(self, debug=False, filename=None):
        self.debug = debug
        self.filename = filename
        self.lang = "ru"
        self.global_scope = Scope()
        self.modules = {}  # имя → dict функций
        self.step_counter = 0
        self._load_builtins()

    def _load_builtins(self):
        """Регистрируем встроенные функции."""
        self.global_scope.vars["цвет"] = self._make_color_module()
        self.global_scope.vars["color"] = self.global_scope.vars["цвет"]

    def _make_color_module(self):
        """Модуль-псевдообъект для цвет.радуга и т.д."""
        return {
            "радуга": lambda args: rainbow(args[0] if args else ""),
            "rainbow": lambda args: rainbow(args[0] if args else ""),
            "огонь": lambda args: fire(args[0] if args else ""),
            "fire": lambda args: fire(args[0] if args else ""),
            "градиент": lambda args: gradient(args[0], args[1], args[2]),
            "gradient": lambda args: gradient(args[0], args[1], args[2]),
            "микс": lambda args: mix(args[0], args[1]),
            "mix": lambda args: mix(args[0], args[1]),
            "палитра": lambda args: show_palette(),
            "palette": lambda args: show_palette(),
        }

    def run(self, program):
        if self.filename:
            try:
                src = Path(self.filename).read_text(encoding="utf-8")
                self.lang = detect_lang(src)
            except: pass

        if self.debug:
            label = "🔍 Дебаг-режим" if self.lang == "ru" else "🔍 Debug mode"
            cprint(label, fg="бирюзовый", styles=["bold"])

        start = time.time()
        for stmt in program.body:
            self.exec_stmt(stmt, self.global_scope)

        if self.debug:
            elapsed = time.time() - start
            msg = f"✅ Завершено за {elapsed:.3f}с" if self.lang == "ru" else f"✅ Done in {elapsed:.3f}s"
            cprint(msg, fg="зелёный")

    # ---------- выполнение операторов ----------
    def exec_stmt(self, stmt, scope):
        if self.debug and hasattr(stmt, 'line'):
            self.step_counter += 1
            self._debug_log(stmt)

        method = getattr(self, f"exec_{type(stmt).__name__}", None)
        if not method:
            raise BRuntimeError(f"Неизвестный узел: {type(stmt).__name__}")
        return method(stmt, scope)

    def _debug_log(self, stmt):
        name = type(stmt).__name__
        label = f"[{self.step_counter}] {name}"
        if hasattr(stmt, 'line'):
            label += f" (строка {stmt.line})"
        cprint(label, fg="серый", styles=["dim"])

    def exec_Let(self, node, scope):
        value = self.eval_expr(node.value, scope) if node.value else None
        # Приведение типа
        if node.type and node.type != "any" and value is not None:
            value = self._coerce(value, node.type, node.line)
        scope.set(node.name, value, type_=node.type, declare=True)

    def exec_Assign(self, node, scope):
        value = self.eval_expr(node.value, scope)
        target = node.target
        if isinstance(target, Name):
            # Проверка типа
            t = scope.get_type(target.name) if scope.has(target.name) else None
            if t and t != "any":
                value = self._coerce(value, t, node.line)
            scope.set(target.name, value)
        elif isinstance(target, Index):
            obj = self.eval_expr(target.obj, scope)
            idx = self.eval_expr(target.idx, scope)
            obj[idx] = value
        elif isinstance(target, Attr):
            obj = self.eval_expr(target.obj, scope)
            if isinstance(obj, BInstance):
                obj.fields[target.attr] = value
            elif isinstance(obj, dict):
                obj[target.attr] = value
            else:
                raise BRuntimeError(f"Нельзя присвоить атрибут {target.attr}", line=node.line)
        else:
            raise BRuntimeError("Невозможное присваивание", line=node.line)

    def exec_Print(self, node, scope):
        parts = []
        skip_print = False
        for a in node.args:
            v = self.eval_expr(a, scope)
            # Если это вызов функции, которая сама что-то напечатала (цвет.радуга и т.п.)
            # и вернула None/пустую строку — не дублируем вывод
            if v is None:
                skip_print = True
                continue
            parts.append(self._stringify(v))

        if skip_print and not parts and not node.fg and not node.bg and not node.styles:
            return

        text = " ".join(parts) if parts else ""
        cprint(text, fg=node.fg, bg=node.bg, styles=node.styles)

    def exec_If(self, node, scope):
        if self._truthy(self.eval_expr(node.cond, scope)):
            self._exec_block(node.body, Scope(scope))
            return
        for econd, ebody in node.elifs:
            if self._truthy(self.eval_expr(econd, scope)):
                self._exec_block(ebody, Scope(scope))
                return
        if node.else_body:
            self._exec_block(node.else_body, Scope(scope))

    def exec_While(self, node, scope):
        while self._truthy(self.eval_expr(node.cond, scope)):
            try:
                self._exec_block(node.body, Scope(scope))
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    def exec_For(self, node, scope):
        if node.iterable is not None:
            it = self.eval_expr(node.iterable, scope)
            for v in it:
                scope.set(node.var, v, declare=True)
                try:
                    self._exec_block(node.body, Scope(scope))
                except BreakSignal: break
                except ContinueSignal: continue
        else:
            start = self.eval_expr(node.start, scope)
            end = self.eval_expr(node.end, scope)
            step = self.eval_expr(node.step, scope) if node.step else 1
            # по умолчанию включительно
            if not node.exclusive:
                if step > 0: end_v = end + 1
                else: end_v = end - 1
            else:
                end_v = end
            for v in range(int(start), int(end_v), int(step)):
                scope.set(node.var, v, declare=True)
                try:
                    self._exec_block(node.body, Scope(scope))
                except BreakSignal: break
                except ContinueSignal: continue

    def _exec_block(self, body, scope):
        for stmt in body:
            self.exec_stmt(stmt, scope)

    def exec_FunctionDef(self, node, scope):
        fn = BFunction(node.name, node.params, node.body, scope)
        scope.set(node.name, fn, declare=True)

    def exec_ClassDef(self, node, scope):
        methods = {}
        attrs = {}
        for stmt in node.body:
            if isinstance(stmt, FunctionDef):
                methods[stmt.name] = BFunction(stmt.name, stmt.params, stmt.body, scope)
            elif isinstance(stmt, Let):
                attrs[stmt.name] = self.eval_expr(stmt.value, scope) if stmt.value else None
        cls = BClass(node.name, methods, attrs)
        scope.set(node.name, cls, declare=True)

    def exec_Return(self, node, scope):
        v = self.eval_expr(node.value, scope) if node.value else None
        raise ReturnSignal(v)

    def exec_Import(self, node, scope):
        from stdlib import load_module
        mod = load_module(node.name)
        if mod is None:
            raise BImportError(
                f"Модуль '{node.name}' не найден",
                line=node.line,
                hint="Доступные: рандом, математика, время, файл, текст, сеть, система, криптография, богатый, вопрос"
            )
        # Регистрируем все имена из модуля в глобальной области
        for ru_name, en_name in mod.get("names", []):
            # Создаём "неймспейс" объект
            pass
        # Регистрируем как объект
        scope.set(node.name, mod["functions"], declare=True)
        # Также регистрируем алиасы имени модуля
        for alias in mod.get("aliases", []):
            scope.set(alias, mod["functions"], declare=True)

    def exec_Try(self, node, scope):
        try:
            self._exec_block(node.body, Scope(scope))
        except BError as e:
            if node.catch_body:
                cs = Scope(scope)
                if node.catch_var:
                    cs.set(node.catch_var, str(e.message), declare=True)
                self._exec_block(node.catch_body, cs)
            else:
                raise
        except Exception as e:
            if node.catch_body:
                cs = Scope(scope)
                if node.catch_var:
                    cs.set(node.catch_var, str(e), declare=True)
                self._exec_block(node.catch_body, cs)
            else:
                raise
        finally:
            if node.finally_body:
                self._exec_block(node.finally_body, Scope(scope))

    def exec_Throw(self, node, scope):
        v = self.eval_expr(node.value, scope)
        raise BRuntimeError(str(v), line=node.line)

    def exec_WarnNode(self, node, scope):
        v = self.eval_expr(node.value, scope)
        handle_warning(str(v), line=node.line, lang=self.lang)

    def exec_Pass(self, node, scope): pass
    def exec_Break(self, node, scope): raise BreakSignal()
    def exec_Continue(self, node, scope): raise ContinueSignal()
    def exec_ExprStmt(self, node, scope): self.eval_expr(node.expr, scope)

    # ---------- выражения ----------
    def eval_expr(self, node, scope):
        method = getattr(self, f"eval_{type(node).__name__}", None)
        if not method:
            raise BRuntimeError(f"Неизвестное выражение: {type(node).__name__}")
        return method(node, scope)

    def eval_Num(self, n, s): return n.value
    def eval_Str(self, n, s):
        if n.has_interp:
            return self._interpolate(n.value, s)
        return n.value
    def eval_Bool(self, n, s): return n.value
    def eval_Null(self, n, s): return None
    def eval_Name(self, n, s): return s.get(n.name)

    def eval_ListLit(self, n, s):
        return [self.eval_expr(i, s) for i in n.items]

    def eval_DictLit(self, n, s):
        return {self.eval_expr(k, s): self.eval_expr(v, s) for k, v in n.pairs}

    def eval_BinOp(self, n, s):
        op = n.op
        l = self.eval_expr(n.left, s)
        if op == "and":
            return self._truthy(l) and self._truthy(self.eval_expr(n.right, s))
        if op == "or":
            return self._truthy(l) or self._truthy(self.eval_expr(n.right, s))
        r = self.eval_expr(n.right, s)
        try:
            if op == "+":
                if isinstance(l, str) or isinstance(r, str):
                    if type(l) != type(r) and not (isinstance(l, str) and isinstance(r, str)):
                        handle_warning(
                            f"Складываешь {self._type_name(l)} и {self._type_name(r)}",
                            line=n.line,
                            hint="Используй 'соединить' или приведи тип",
                            lang=self.lang
                        )
                    return str(l) + str(r)
                return l + r
            if op == "-": return l - r
            if op == "*":
                if isinstance(l, str) and isinstance(r, int): return l * r
                if isinstance(r, str) and isinstance(l, int): return r * l
                return l * r
            if op == "/":
                if r == 0:
                    raise BRuntimeError("Деление на ноль", line=n.line,
                                        hint="Проверь знаменатель")
                return l / r
            if op == "%": return l % r
            if op == "==": return l == r
            if op == "!=": return l != r
            if op == "<": return l < r
            if op == ">": return l > r
            if op == "<=": return l <= r
            if op == ">=": return l >= r
        except BError:
            raise
        except Exception as e:
            raise BRuntimeError(f"Ошибка операции {op}: {e}", line=n.line)

    def eval_UnaryOp(self, n, s):
        v = self.eval_expr(n.operand, s)
        if n.op == "-": return -v
        if n.op == "not": return not self._truthy(v)
        return v

    def eval_Attr(self, n, s):
        obj = self.eval_expr(n.obj, s)
        if isinstance(obj, dict):
            if n.attr in obj:
                return obj[n.attr]
            raise BNameError(f"Нет атрибута '{n.attr}'", line=n.line)
        if isinstance(obj, BInstance):
            if n.attr in obj.fields:
                return obj.fields[n.attr]
            if n.attr in obj.cls.methods:
                return ("method", obj, obj.cls.methods[n.attr])
            raise BNameError(f"Нет атрибута '{n.attr}' у {obj.cls.name}", line=n.line)
        # Строковые методы
        if isinstance(obj, str):
            m = _str_method(obj, n.attr)
            if m is not None: return m
        if isinstance(obj, list):
            m = _list_method(obj, n.attr)
            if m is not None: return m
        raise BNameError(f"Нет атрибута '{n.attr}'", line=n.line)

    def eval_Index(self, n, s):
        obj = self.eval_expr(n.obj, s)
        idx = self.eval_expr(n.idx, s)
        try:
            return obj[idx]
        except Exception as e:
            raise BRuntimeError(f"Ошибка индексации: {e}", line=n.line)

    def eval_Call(self, n, s):
        func = self.eval_expr(n.func, s)
        args = [self.eval_expr(a, s) for a in n.args]
        return self._call(func, args, n.line)

    def eval_InputExpr(self, n, s):
        prompt = self.eval_expr(n.prompt, s) if n.prompt else ""
        try:
            raw = input(str(prompt))
        except (EOFError, KeyboardInterrupt):
            return ""
        return raw  # возвращаем строку; приведение сделает Let

    # ---------- вспомогательные ----------
    def _call(self, func, args, line):
        if isinstance(func, BFunction):
            scope = Scope(func.closure)
            for (pname, ptype), val in zip(func.params, args):
                if ptype and ptype != "any":
                    val = self._coerce(val, ptype, line)
                scope.set(pname, val, type_=ptype, declare=True)
            try:
                self._exec_block(func.body, scope)
            except ReturnSignal as r:
                return r.value
            return None
        if isinstance(func, BClass):
            inst = BInstance(func)
            if "инит" in func.methods or "init" in func.methods:
                init = func.methods.get("инит") or func.methods.get("init")
                scope = Scope(init.closure)
                scope.set("я", inst, declare=True)
                scope.set("self", inst, declare=True)
                for (pname, ptype), val in zip(init.params, args):
                    scope.set(pname, val, type_=ptype, declare=True)
                try:
                    self._exec_block(init.body, scope)
                except ReturnSignal: pass
            return inst
        if isinstance(func, tuple) and func[0] == "method":
            _, inst, bfn = func
            scope = Scope(bfn.closure)
            scope.set("я", inst, declare=True)
            scope.set("self", inst, declare=True)
            for (pname, ptype), val in zip(bfn.params, args):
                scope.set(pname, val, type_=ptype, declare=True)
            try:
                self._exec_block(bfn.body, scope)
            except ReturnSignal as r:
                return r.value
            return None
        if callable(func):
            # Python-функция (из stdlib или встроенная)
            try:
                return func(args)
            except TypeError:
                return func(*args)
        if isinstance(func, dict):
            raise BRuntimeError(
                "Пытаешься вызвать модуль как функцию. Используй модуль.функция",
                line=line
            )
        raise BRuntimeError(f"Нельзя вызвать {type(func).__name__}", line=line)

    def _coerce(self, value, type_, line=None):
        try:
            if type_ == "number":
                if isinstance(value, bool): return int(value)
                if isinstance(value, (int, float)): return value
                if isinstance(value, str):
                    v = value.strip()
                    if "." in v: return float(v)
                    return int(v)
                return 0
            if type_ == "string":
                return str(value)
            if type_ == "bool":
                return bool(value) and value not in ("", "ложь", "false", "0", 0)
            if type_ == "list":
                if isinstance(value, list): return value
                return list(value)
            if type_ == "dict":
                if isinstance(value, dict): return value
                return dict(value)
            return value
        except Exception:
            handle_warning(
                f"Не удалось привести {type(value).__name__} к {type_}",
                line=line, lang=self.lang
            )
            return value

    def _truthy(self, v):
        if v is None: return False
        if isinstance(v, bool): return v
        if isinstance(v, (int, float)): return v != 0
        if isinstance(v, str): return len(v) > 0
        if isinstance(v, (list, dict)): return len(v) > 0
        return bool(v)

    def _stringify(self, v):
        if v is None: return "ничего"
        if v is True: return "истина"
        if v is False: return "ложь"
        return str(v)

    def _type_name(self, v):
        if isinstance(v, bool): return "бул"
        if isinstance(v, int): return "число"
        if isinstance(v, float): return "число"
        if isinstance(v, str): return "строка"
        if isinstance(v, list): return "список"
        if isinstance(v, dict): return "словарь"
        return type(v).__name__

    def _interpolate(self, s, scope):
        """f-строки без f: {выражение} с поддержкой любых вычислений."""
        import re
        def repl(m):
            expr = m.group(1).strip()
            try:
                # Токенизируем внутренности скобок
                tokens = tokenize(expr)
                # Фильтруем служебные токены отступов и переносов
                filtered_tokens = [t for t in tokens if t.type not in (TokType.INDENT, TokType.NEWLINE)]

                ast = Parser(filtered_tokens)
                node = ast.parse_expr()
                return self._stringify(self.eval_expr(node, scope))
            except Exception as e:
                if self.debug:
                    print(f"DEBUG Interpolation Error: {e}")
                return "{" + expr + "}"
        return re.sub(r"\{([^{}]+)\}", repl, s)


# ===== Методы строк/списков =====
def _str_method(s, name):
    name = name.lower()
    if name in ("длина", "len"): return len(s)
    if name in ("верх", "upper"): return lambda args: s.upper()
    if name in ("низ", "lower"): return lambda args: s.lower()
    if name in ("обрезать", "trim", "strip"): return lambda args: s.strip()
    if name in ("разбить", "split"): return lambda args: s.split(args[0] if args else None)
    if name in ("заменить", "replace"): return lambda args: s.replace(args[0], args[1])
    return None

def _list_method(lst, name):
    name = name.lower()
    if name in ("длина", "len"): return len(lst)
    if name in ("добавить", "push", "append"):
        def _push(args):
            for a in args: lst.append(a)
            return lst
        return _push
    if name in ("убрать", "pop"):
        return lambda args: lst.pop(args[0] if args else -1)
    if name in ("сортировать", "sort"):
        return lambda args: sorted(lst)
    return None
