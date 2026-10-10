"""Лексер b — токенизирует исходный код."""
import re
from core.errors import BSyntaxError

# Типы токенов
class TokType:
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENT = "IDENT"
    OP = "OP"
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    COMMA = "COMMA"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACK = "LBRACK"
    RBRACK = "RBRACK"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    DOT = "DOT"
    COLON = "COLON"
    AMP = "AMP"           # && — разделитель команд в строке
    RANGE = "RANGE"       # ..
    ASSIGN = "ASSIGN"     # =
    EOF = "EOF"

class Token:
    __slots__ = ("type", "value", "line", "col")
    def __init__(self, type, value, line=1, col=1):
        self.type = type
        self.value = value
        self.line = line
        self.col = col
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, L{self.line})"

# Операторы (символьные)
MULTI_CHAR_OPS = ["==", "!=", "<=", ">=", "&&", "||", "..", "->"]
SINGLE_OPS = set("+-*/%<>=!")

def tokenize(src):
    """Разбивает исходник на токены."""
    tokens = []
    lines = src.split("\n")

    for lineno, line in enumerate(lines, 1):
        # Убираем комментарии (но не в строках!)
        line_clean = _strip_comment(line)

        if not line_clean.strip():
            tokens.append(Token(TokType.NEWLINE, "\\n", lineno, 1))
            continue

        # Отступ
        indent = len(line_clean) - len(line_clean.lstrip(" \t"))
        # Нормализуем табы -> 4 пробела
        indent_str = line_clean[:indent].replace("\t", "    ")
        tokens.append(Token(TokType.INDENT, len(indent_str), lineno, 1))

        _tokenize_line(line_clean.lstrip(" \t"), lineno, indent + 1, tokens)
        tokens.append(Token(TokType.NEWLINE, "\\n", lineno, len(line) + 1))

    tokens.append(Token(TokType.EOF, None, len(lines), 1))
    return tokens

def _strip_comment(line):
    """Удаляет комментарий // (не внутри строк)."""
    i = 0
    in_str = None
    while i < len(line):
        ch = line[i]
        if in_str:
            if ch == "\\" and i + 1 < len(line):
                i += 2
                continue
            if ch == in_str:
                in_str = None
        else:
            if ch in ('"', "'"):
                # Проверка на тройные
                if line[i:i+3] in ('"""', "'''"):
                    # Пропускаем всё до конца или закрытия на этой же строке
                    quote = line[i:i+3]
                    end = line.find(quote, i + 3)
                    if end == -1:
                        return line  # многострочная — обработается отдельно
                    i = end + 3
                    continue
                in_str = ch
            elif ch == "/" and i + 1 < len(line) and line[i+1] == "/":
                return line[:i]
        i += 1
    return line

def _tokenize_line(line, lineno, start_col, tokens):
    i = 0
    while i < len(line):
        ch = line[i]
        col = start_col + i

        # Пробелы
        if ch in " \t":
            i += 1
            continue

        # Многострочная строка
        if line[i:i+3] in ('"""', "'''"):
            quote = line[i:i+3]
            end = line.find(quote, i + 3)
            if end == -1:
                # Собираем многострочную (упрощённо — читаем до конца файла в parser,
                # но здесь поддержим только однострочную тройную)
                raise BSyntaxError(
                    "Многострочные строки должны закрываться на той же строке в текущей версии",
                    line=lineno,
                    hint="Используй \\n внутри обычной строки"
                )
            content = line[i+3:end]
            tokens.append(Token(TokType.STRING, content, lineno, col))
            i = end + 3
            continue

        # Строки
        if ch in ('"', "'"):
            quote = ch
            j = i + 1
            buf = []
            while j < len(line) and line[j] != quote:
                if line[j] == "\\" and j + 1 < len(line):
                    nxt = line[j+1]
                    esc = {"n":"\n","t":"\t","r":"\r","\\":"\\",
                           '"':'"',"'":"'","0":"\0"}
                    buf.append(esc.get(nxt, nxt))
                    j += 2
                else:
                    buf.append(line[j])
                    j += 1
            if j >= len(line):
                raise BSyntaxError(
                    f"Незакрытая строка",
                    line=lineno,
                    hint="Добавь закрывающую кавычку",
                    code=line
                )
            tokens.append(Token(TokType.STRING, "".join(buf), lineno, col))
            i = j + 1
            continue

        # Числа
        if ch.isdigit() or (ch == "." and i+1 < len(line) and line[i+1].isdigit()):
            j = i
            has_dot = False
            while j < len(line) and (line[j].isdigit() or line[j] == "."):
                if line[j] == ".":
                    # Проверка на .. (range)
                    if j + 1 < len(line) and line[j+1] == ".":
                        break
                    if has_dot:
                        break
                    has_dot = True
                j += 1
            num_str = line[i:j]
            val = float(num_str) if has_dot else int(num_str)
            tokens.append(Token(TokType.NUMBER, val, lineno, col))
            i = j
            continue

        # Идентификаторы (буквы, цифры, _, кириллица)
        if ch.isalpha() or ch == "_" or _is_cyrillic(ch):
            j = i
            while j < len(line) and (line[j].isalnum() or line[j] == "_" or _is_cyrillic(line[j])):
                j += 1
            tokens.append(Token(TokType.IDENT, line[i:j], lineno, col))
            i = j
            continue

        # Многосимвольные операторы
        two = line[i:i+2]
        if two == "..":
            tokens.append(Token(TokType.RANGE, "..", lineno, col))
            i += 2
            continue
        if two == "&&":
            tokens.append(Token(TokType.AMP, "&&", lineno, col))
            i += 2
            continue
        if two in ("==", "!=", "<=", ">=", "||", "->"):
            tokens.append(Token(TokType.OP, two, lineno, col))
            i += 2
            continue

        # Односимвольные
        if ch == ",":
            tokens.append(Token(TokType.COMMA, ",", lineno, col))
        elif ch == "(":
            tokens.append(Token(TokType.LPAREN, "(", lineno, col))
        elif ch == ")":
            tokens.append(Token(TokType.RPAREN, ")", lineno, col))
        elif ch == "[":
            tokens.append(Token(TokType.LBRACK, "[", lineno, col))
        elif ch == "]":
            tokens.append(Token(TokType.RBRACK, "]", lineno, col))
        elif ch == "{":
            tokens.append(Token(TokType.LBRACE, "{", lineno, col))
        elif ch == "}":
            tokens.append(Token(TokType.RBRACE, "}", lineno, col))
        elif ch == ".":
            tokens.append(Token(TokType.DOT, ".", lineno, col))
        elif ch == ":":
            tokens.append(Token(TokType.COLON, ":", lineno, col))
        elif ch == "=":
            tokens.append(Token(TokType.ASSIGN, "=", lineno, col))
        elif ch == "#":
            # Hex-цвет вида #FFA500 — токенизируем как строку
            j = i + 1
            while j < len(line) and line[j].isalnum():
                j += 1
            hex_str = line[i:j]
            tokens.append(Token(TokType.STRING, hex_str, lineno, col))
            i = j
            continue
        elif ch in SINGLE_OPS:
            tokens.append(Token(TokType.OP, ch, lineno, col))
        else:
            raise BSyntaxError(
                f"Неизвестный символ: {ch!r}",
                line=lineno,
                hint="Проверь символ или используй другой"
            )
        i += 1

def _is_cyrillic(ch):
    return 'а' <= ch.lower() <= 'я' or ch == 'ё' or ch == 'Ё'
