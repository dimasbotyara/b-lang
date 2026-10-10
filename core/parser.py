"""Парсер b — строит AST из токенов."""
from core.lexer import TokType, Token
from core.errors import BSyntaxError
from core.keywords import *
from core import keywords as KW

# ===== Узлы AST =====
class Node: pass

class Program(Node):
    def __init__(self, body): self.body = body

class Let(Node):
    def __init__(self, name, type_, value, line):
        self.name, self.type, self.value, self.line = name, type_, value, line

class Assign(Node):
    def __init__(self, target, value, line):
        self.target, self.value, self.line = target, value, line

class Print(Node):
    def __init__(self, args, fg, bg, styles, line):
        self.args, self.fg, self.bg, self.styles, self.line = args, fg, bg, styles, line

class If(Node):
    def __init__(self, cond, body, elifs, else_body, line):
        self.cond, self.body, self.elifs, self.else_body, self.line = cond, body, elifs, else_body, line

class While(Node):
    def __init__(self, cond, body, line):
        self.cond, self.body, self.line = cond, body, line

class For(Node):
    def __init__(self, var, start, end, step, exclusive, iterable, body, line):
        self.var, self.start, self.end, self.step = var, start, end, step
        self.exclusive, self.iterable, self.body, self.line = exclusive, iterable, body, line

class FunctionDef(Node):
    def __init__(self, name, params, body, line):
        self.name, self.params, self.body, self.line = name, params, body, line

class ClassDef(Node):
    def __init__(self, name, body, line):
        self.name, self.body, self.line = name, body, line

class Return(Node):
    def __init__(self, value, line):
        self.value, self.line = value, line

class Import(Node):
    def __init__(self, name, line):
        self.name, self.line = name, line

class Try(Node):
    def __init__(self, body, catch_var, catch_body, finally_body, line):
        self.body = body
        self.catch_var = catch_var
        self.catch_body = catch_body
        self.finally_body = finally_body
        self.line = line

class Throw(Node):
    def __init__(self, value, line):
        self.value, self.line = value, line

class WarnNode(Node):
    def __init__(self, value, line):
        self.value, self.line = value, line

class Pass(Node):
    def __init__(self, line): self.line = line

class Break(Node):
    def __init__(self, line): self.line = line

class Continue(Node):
    def __init__(self, line): self.line = line

class BinOp(Node):
    def __init__(self, op, left, right, line):
        self.op, self.left, self.right, self.line = op, left, right, line

class UnaryOp(Node):
    def __init__(self, op, operand, line):
        self.op, self.operand, self.line = op, operand, line

class Num(Node):
    def __init__(self, value, line): self.value, self.line = value, line

class Str(Node):
    def __init__(self, value, line, has_interp=False):
        self.value, self.line, self.has_interp = value, line, has_interp

class Bool(Node):
    def __init__(self, value, line): self.value, self.line = value, line

class Null(Node):
    def __init__(self, line): self.line = line

class Name(Node):
    def __init__(self, name, line): self.name, self.line = name, line

class ListLit(Node):
    def __init__(self, items, line): self.items, self.line = items, line

class DictLit(Node):
    def __init__(self, pairs, line): self.pairs, self.line = pairs, line

class Index(Node):
    def __init__(self, obj, idx, line): self.obj, self.idx, self.line = obj, idx, line

class Attr(Node):
    def __init__(self, obj, attr, line): self.obj, self.attr, self.line = obj, attr, line

class Call(Node):
    def __init__(self, func, args, line):
        self.func, self.args, self.line = func, args, line

class InputExpr(Node):
    def __init__(self, prompt, strict, default, line):
        self.prompt, self.strict, self.default, self.line = prompt, strict, default, line

class ExprStmt(Node):
    def __init__(self, expr, line): self.expr, self.line = expr, line


# ===== Парсер =====
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---------- утилиты ----------
    def peek(self, offset=0):
        return self.tokens[self.pos + offset] if self.pos + offset < len(self.tokens) else self.tokens[-1]

    def advance(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def match(self, type_, value=None):
        t = self.peek()
        if t.type != type_:
            return False
        if value is not None:
            if isinstance(value, set):
                return t.value is not None and str(t.value).lower() in value
            return t.value == value
        return True

    def consume(self, type_, value=None, msg=None):
        if not self.match(type_, value):
            t = self.peek()
            raise BSyntaxError(
                msg or f"Ожидался {type_} {value}, получено {t.type} {t.value!r}",
                line=t.line
            )
        return self.advance()

    def eat_newlines(self):
        while self.peek().type == TokType.NEWLINE or self.peek().type == TokType.INDENT:
            # INDENT без последующего значимого содержимого — пропустить
            if self.peek().type == TokType.INDENT:
                nxt = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                if nxt and nxt.type == TokType.NEWLINE:
                    self.advance()
                    self.advance()
                    continue
                return
            self.advance()

    def current_indent(self):
        """Возвращает отступ текущей строки (если указатель на INDENT)."""
        t = self.peek()
        if t.type == TokType.INDENT:
            return t.value
        return None

    # ---------- parse ----------
    def parse(self):
        body = []
        self.eat_newlines()
        while self.peek().type != TokType.EOF:
            stmts = self.parse_statement_line(parent_indent=-1)
            if stmts:
                body.extend(stmts if isinstance(stmts, list) else [stmts])
            self.eat_newlines()
        return Program(body)

    def parse_block(self, parent_indent):
        """Парсит блок — строки с отступом > parent_indent."""
        body = []
        self.eat_newlines()
        while self.peek().type != TokType.EOF:
            ind = self.current_indent()
            if ind is None or ind <= parent_indent:
                break
            stmts = self.parse_statement_line(parent_indent=ind)
            if stmts:
                body.extend(stmts if isinstance(stmts, list) else [stmts])
            self.eat_newlines()
        if not body:
            # Пустой блок — вставим Pass
            body.append(Pass(self.peek().line))
        return body

    def parse_statement_line(self, parent_indent):
        """Парсит одну логическую строку (может содержать && — несколько операторов)."""
        # Пропускаем INDENT
        if self.peek().type == TokType.INDENT:
            self.advance()

        # Пустая строка?
        if self.peek().type == TokType.NEWLINE:
            self.advance()
            return []

        stmts = [self.parse_statement(parent_indent)]
        while self.peek().type == TokType.AMP:
            self.advance()
            stmts.append(self.parse_statement(parent_indent))

        # Съесть newline
        if self.peek().type == TokType.NEWLINE:
            self.advance()
        return stmts

    def parse_statement(self, parent_indent):
        t = self.peek()

        if t.type == TokType.IDENT:
            w = t.value.lower()
            if w in LET:
                return self.parse_let()
            if w in PRINT:
                return self.parse_print()
            if w in IF:
                return self.parse_if(parent_indent)
            if w in WHILE:
                return self.parse_while(parent_indent)
            if w in FOR:
                return self.parse_for(parent_indent)
            if w in FUNCTION:
                return self.parse_function(parent_indent)
            if w in CLASS:
                return self.parse_class(parent_indent)
            if w in RETURN:
                return self.parse_return()
            if w in IMPORT:
                return self.parse_import()
            if w in TRY:
                return self.parse_try(parent_indent)
            if w in THROW:
                return self.parse_throw()
            if w in WARN:
                return self.parse_warn()
            if w in PASS:
                self.advance()
                return Pass(t.line)
            if w in BREAK:
                self.advance()
                return Break(t.line)
            if w in CONTINUE:
                self.advance()
                return Continue(t.line)

        # Присваивание или выражение
        return self.parse_assign_or_expr()

    # ---------- конкретные конструкции ----------
    def parse_let(self):
        line = self.peek().line
        self.advance()  # let
        name_tok = self.consume(TokType.IDENT)
        name = name_tok.value
        type_ = "any"
        # Опциональный тип
        if self.peek().type == TokType.IDENT and self.peek().value.lower() in TYPES:
            type_ = KW.normalize_type(self.advance().value)
        value = None
        if self.peek().type == TokType.ASSIGN:
            self.advance()
            value = self.parse_expr()
        return Let(name, type_, value, line)

    def parse_assign_or_expr(self):
        line = self.peek().line
        expr = self.parse_expr()
        if self.peek().type == TokType.ASSIGN:
            self.advance()
            value = self.parse_expr()
            return Assign(expr, value, line)
        return ExprStmt(expr, line)

    def parse_print(self):
        line = self.peek().line
        self.advance()  # print
        args = []
        fg, bg, styles = None, None, []

        # Собираем выражения, пока не наткнёмся на модификатор или терминатор
        if not self._is_print_terminator() and not self._is_print_modifier():
            args.append(self.parse_expr())
            while self.peek().type == TokType.COMMA:
                self.advance()
                if self._is_print_terminator() or self._is_print_modifier():
                    break
                args.append(self.parse_expr())

        # Разбор модификаторов (цвет / стили / фон)
        while self._is_print_modifier():
            w = self.peek().value.lower()
            if w in COLOR:
                self.advance()
                fg = self._parse_color_value()
            elif w in BG:
                self.advance()
                bg = self._parse_color_value()
            elif w in STYLES:
                styles.append(self.advance().value.lower())
            else:
                break

        return Print(args, fg, bg, styles, line)

    def _is_print_terminator(self):
        t = self.peek()
        return t.type in (TokType.NEWLINE, TokType.EOF, TokType.AMP)

    def _is_print_modifier(self):
        """Проверяет, является ли следующий токен модификатором печати (цвет/фон/стиль).

        Важно: 'цвет.радуга' — это НЕ модификатор, а обращение к атрибуту!
        Если после ключевого слова идёт точка — это выражение.
        """
        t = self.peek()
        if t.type != TokType.IDENT:
            return False
        w = t.value.lower()

        if w not in COLOR and w not in BG and w not in STYLES:
            return False

        # Смотрим вперёд — если дальше точка, то это обращение к атрибуту (цвет.радуга)
        nxt = self.peek(1)
        if nxt and nxt.type == TokType.DOT:
            return False

        # Также: если это 'цвет'/'color' и дальше скобка — это тоже вызов функции
        if nxt and nxt.type == TokType.LPAREN:
            return False

        return True

    def _parse_color_value(self):
        """Парсит имя цвета, #hex, rgb R,G,B."""
        t = self.peek()
        # rgb R,G,B
        if t.type == TokType.IDENT and t.value.lower() == "rgb":
            self.advance()
            r = int(self.consume(TokType.NUMBER).value)
            self.consume(TokType.COMMA)
            g = int(self.consume(TokType.NUMBER).value)
            self.consume(TokType.COMMA)
            b = int(self.consume(TokType.NUMBER).value)
            return f"rgb({r},{g},{b})"
        # #hex — но # не токен. Проверим: если OP "#"? Хак: будем принимать строку.
        # Либо имя (ident)
        if t.type == TokType.IDENT:
            return self.advance().value
        if t.type == TokType.STRING:
            return self.advance().value
        if t.type == TokType.OP and t.value == "#":
            # unlikely path
            self.advance()
            # собрать hex
            nxt = self.advance()
            return "#" + str(nxt.value)
        # Если число — может быть hex подобие? Пропускаем
        raise BSyntaxError(
            f"Ожидался цвет, получено {t.value!r}",
            line=t.line,
            hint="Используй имя (красный), #FF0000 или rgb 255,0,0"
        )

    def parse_if(self, parent_indent):
        line = self.peek().line
        self.advance()  # if
        cond = self.parse_expr()
        body = self.parse_block(parent_indent)
        elifs = []
        else_body = None

        # elif/else
        self.eat_newlines()
        while True:
            ind = self.current_indent()
            if ind != parent_indent and parent_indent != -1:
                # для верхнеуровневых if parent_indent == -1, но строка начинается с 0
                if ind is None or (parent_indent == -1 and ind > 0):
                    break
                if parent_indent != -1 and ind != parent_indent:
                    break
            # Для -1 ожидаем ind == 0
            if parent_indent == -1 and ind != 0:
                break

            save_pos = self.pos
            if self.peek().type == TokType.INDENT:
                self.advance()
            t = self.peek()
            if t.type == TokType.IDENT and t.value.lower() in ELSE:
                self.advance()
                # Может быть "иначе если"
                if self.peek().type == TokType.IDENT and self.peek().value.lower() in IF:
                    self.advance()
                    econd = self.parse_expr()
                    ebody = self.parse_block(parent_indent if parent_indent != -1 else 0)
                    elifs.append((econd, ebody))
                    self.eat_newlines()
                    continue
                else:
                    else_body = self.parse_block(parent_indent if parent_indent != -1 else 0)
                    break
            elif t.type == TokType.IDENT and t.value.lower() in ELIF:
                self.advance()
                econd = self.parse_expr()
                ebody = self.parse_block(parent_indent if parent_indent != -1 else 0)
                elifs.append((econd, ebody))
                self.eat_newlines()
                continue
            else:
                self.pos = save_pos
                break

        return If(cond, body, elifs, else_body, line)

    def parse_while(self, parent_indent):
        line = self.peek().line
        self.advance()
        cond = self.parse_expr()
        body = self.parse_block(parent_indent)
        return While(cond, body, line)

    def parse_for(self, parent_indent):
        line = self.peek().line
        self.advance()  # for
        var = self.consume(TokType.IDENT).value
        # в / in
        if not (self.peek().type == TokType.IDENT and self.peek().value.lower() in IN):
            raise BSyntaxError("Ожидалось 'в' или 'in'", line=self.peek().line)
        self.advance()

        start = self.parse_expr()
        end = None
        step = None
        exclusive = False
        iterable = None

        if self.peek().type == TokType.RANGE:
            self.advance()
            end = self.parse_expr()
            # опции
            while self.peek().type == TokType.IDENT:
                w = self.peek().value.lower()
                if w in STEP:
                    self.advance()
                    step = self.parse_expr()
                elif w in EXCLUSIVE:
                    self.advance()
                    exclusive = True
                else:
                    break
        elif self.peek().type == TokType.COMMA:
            # для i в 1, 10 — тоже поддержим
            self.advance()
            end = self.parse_expr()
            if self.peek().type == TokType.COMMA:
                self.advance()
                step = self.parse_expr()
        else:
            # Итерация по списку/строке
            iterable = start
            start = None

        body = self.parse_block(parent_indent)
        return For(var, start, end, step, exclusive, iterable, body, line)

    def parse_function(self, parent_indent):
        line = self.peek().line
        self.advance()
        name = self.consume(TokType.IDENT).value
        params = []
        # параметры: имя [тип], ...
        while self.peek().type == TokType.IDENT and self.peek().value.lower() not in {"конец"}:
            if self.peek().type == TokType.NEWLINE:
                break
            pname = self.advance().value
            ptype = "any"
            if self.peek().type == TokType.IDENT and self.peek().value.lower() in TYPES:
                ptype = KW.normalize_type(self.advance().value)
            params.append((pname, ptype))
            if self.peek().type == TokType.COMMA:
                self.advance()
            else:
                break
        body = self.parse_block(parent_indent)
        return FunctionDef(name, params, body, line)

    def parse_class(self, parent_indent):
        line = self.peek().line
        self.advance()
        name = self.consume(TokType.IDENT).value
        body = self.parse_block(parent_indent)
        return ClassDef(name, body, line)

    def parse_return(self):
        line = self.peek().line
        self.advance()
        value = None
        if not self._is_print_terminator():
            value = self.parse_expr()
        return Return(value, line)

    def parse_import(self):
        line = self.peek().line
        self.advance()
        name = self.consume(TokType.IDENT).value
        return Import(name, line)

    def parse_try(self, parent_indent):
        line = self.peek().line
        self.advance()  # try
        body = self.parse_block(parent_indent)
        catch_var = None
        catch_body = None
        finally_body = None
        self.eat_newlines()
        while True:
            ind = self.current_indent()
            if ind is None:
                break
            save_pos = self.pos
            if self.peek().type == TokType.INDENT:
                self.advance()
            t = self.peek()
            if t.type == TokType.IDENT and t.value.lower() in CATCH:
                self.advance()
                if self.peek().type == TokType.IDENT:
                    catch_var = self.advance().value
                catch_body = self.parse_block(parent_indent if parent_indent != -1 else 0)
                self.eat_newlines()
                continue
            if t.type == TokType.IDENT and t.value.lower() in FINALLY:
                self.advance()
                finally_body = self.parse_block(parent_indent if parent_indent != -1 else 0)
                break
            self.pos = save_pos
            break
        return Try(body, catch_var, catch_body, finally_body, line)

    def parse_throw(self):
        line = self.peek().line
        self.advance()
        value = self.parse_expr()
        return Throw(value, line)

    def parse_warn(self):
        line = self.peek().line
        self.advance()
        value = self.parse_expr()
        return WarnNode(value, line)

    # ---------- выражения ----------
    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while (self.peek().type == TokType.OP and self.peek().value == "||") or \
              (self.peek().type == TokType.IDENT and self.peek().value.lower() in OR):
            op = self.advance()
            right = self.parse_and()
            left = BinOp("or", left, right, op.line)
        return left

    def parse_and(self):
        left = self.parse_not()
        while (self.peek().type == TokType.OP and self.peek().value == "&&") or \
              (self.peek().type == TokType.IDENT and self.peek().value.lower() in AND):
            # Внимание: && без контекста конца — это конкатенатор. Внутри выражения — AND.
            # Используем AND только слово. && не трогаем здесь.
            if self.peek().type == TokType.OP and self.peek().value == "&&":
                # не AND — это разделитель команд! Выходим.
                break
            if self.peek().value.lower() not in AND:
                break
            op = self.advance()
            right = self.parse_not()
            left = BinOp("and", left, right, op.line)
        return left

    def parse_not(self):
        if self.peek().type == TokType.IDENT and self.peek().value.lower() in NOT:
            tok = self.advance()
            operand = self.parse_not()
            return UnaryOp("not", operand, tok.line)
        return self.parse_cmp()

    def parse_cmp(self):
        left = self.parse_add()
        while True:
            t = self.peek()
            op = None
            if t.type == TokType.OP and t.value in ("==", "!=", "<", ">", "<=", ">="):
                op = t.value
                self.advance()
            elif t.type == TokType.IDENT and t.value.lower() in EQ:
                self.advance(); op = "=="
            elif t.type == TokType.IDENT and t.value.lower() in NEQ:
                self.advance(); op = "!="
            elif t.type == TokType.IDENT and t.value.lower() in GT:
                self.advance(); op = ">"
            elif t.type == TokType.IDENT and t.value.lower() in LT:
                self.advance(); op = "<"
            elif t.type == TokType.IDENT and t.value.lower() in GTE:
                self.advance(); op = ">="
            elif t.type == TokType.IDENT and t.value.lower() in LTE:
                self.advance(); op = "<="
            else:
                break
            right = self.parse_add()
            left = BinOp(op, left, right, t.line)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while True:
            t = self.peek()
            op = None
            if t.type == TokType.OP and t.value in ("+", "-"):
                op = t.value
                self.advance()
            elif t.type == TokType.IDENT and t.value.lower() in ADD:
                self.advance(); op = "+"
            elif t.type == TokType.IDENT and t.value.lower() in SUB:
                self.advance(); op = "-"
            else:
                break
            right = self.parse_mul()
            left = BinOp(op, left, right, t.line)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while True:
            t = self.peek()
            op = None
            if t.type == TokType.OP and t.value in ("*", "/", "%"):
                op = t.value
                self.advance()
            elif t.type == TokType.IDENT and t.value.lower() in MUL:
                self.advance(); op = "*"
            elif t.type == TokType.IDENT and t.value.lower() in DIV:
                self.advance(); op = "/"
            elif t.type == TokType.IDENT and t.value.lower() in MOD:
                self.advance(); op = "%"
            else:
                break
            right = self.parse_unary()
            left = BinOp(op, left, right, t.line)
        return left

    def parse_unary(self):
        t = self.peek()
        if t.type == TokType.OP and t.value == "-":
            self.advance()
            operand = self.parse_unary()
            return UnaryOp("-", operand, t.line)
        if t.type == TokType.OP and t.value == "+":
            self.advance()
            return self.parse_unary()
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            t = self.peek()
            if t.type == TokType.DOT:
                self.advance()
                attr = self.consume(TokType.IDENT).value
                expr = Attr(expr, attr, t.line)
            elif t.type == TokType.LBRACK:
                self.advance()
                idx = self.parse_expr()
                self.consume(TokType.RBRACK)
                expr = Index(expr, idx, t.line)
            elif t.type == TokType.LPAREN:
                self.advance()
                args = []
                if self.peek().type != TokType.RPAREN:
                    args.append(self.parse_expr())
                    while self.peek().type == TokType.COMMA:
                        self.advance()
                        args.append(self.parse_expr())
                self.consume(TokType.RPAREN)
                expr = Call(expr, args, t.line)
            else:
                break
        return expr

    def parse_primary(self):
        t = self.peek()

        if t.type == TokType.NUMBER:
            self.advance()
            return Num(t.value, t.line)

        if t.type == TokType.STRING:
            self.advance()
            has_interp = "{" in t.value and "}" in t.value
            return Str(t.value, t.line, has_interp)

        if t.type == TokType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.consume(TokType.RPAREN)
            return expr

        if t.type == TokType.LBRACK:
            self.advance()
            items = []
            if self.peek().type != TokType.RBRACK:
                items.append(self.parse_expr())
                while self.peek().type == TokType.COMMA:
                    self.advance()
                    items.append(self.parse_expr())
            self.consume(TokType.RBRACK)
            return ListLit(items, t.line)

        if t.type == TokType.LBRACE:
            self.advance()
            pairs = []
            if self.peek().type != TokType.RBRACE:
                while True:
                    k = self.parse_expr()
                    self.consume(TokType.COLON)
                    v = self.parse_expr()
                    pairs.append((k, v))
                    if self.peek().type == TokType.COMMA:
                        self.advance()
                    else:
                        break
            self.consume(TokType.RBRACE)
            return DictLit(pairs, t.line)

        if t.type == TokType.IDENT:
            w = t.value.lower()
            if w in TRUE:
                self.advance()
                return Bool(True, t.line)
            if w in FALSE:
                self.advance()
                return Bool(False, t.line)
            if w in NULL:
                self.advance()
                return Null(t.line)
            if w in INPUT:
                self.advance()
                prompt = None
                strict = False
                default = None
                if self.peek().type == TokType.STRING or self.peek().type == TokType.IDENT:
                    # вытягиваем prompt как первое выражение
                    if not (self.peek().type == TokType.IDENT and
                            self.peek().value.lower() in (STRICT | OR | AND)):
                        prompt = self.parse_expr_no_mod()
                # модификаторы
                while self.peek().type == TokType.IDENT:
                    w2 = self.peek().value.lower()
                    if w2 in STRICT:
                        self.advance()
                        strict = True
                    elif w2 in OR:
                        self.advance()
                        default = self.parse_expr_no_mod()
                    else:
                        break
                return InputExpr(prompt, strict, default, t.line)
            self.advance()
            return Name(t.value, t.line)

        raise BSyntaxError(f"Неожиданный токен: {t.value!r}", line=t.line)

    def parse_expr_no_mod(self):
        """Для контекстов где нельзя парсить модификаторы."""
        return self.parse_add()
