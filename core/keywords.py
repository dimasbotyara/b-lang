"""Все ключевые слова языка b на двух языках."""

# Объявление переменных
LET = {"пусть", "let", "объявить"}

# Печать
PRINT = {"печать", "print", "вывести"}

# Условия
IF = {"если", "if"}
ELSE = {"иначе", "else"}
ELIF = {"иначе_если", "elif"}

# Циклы
WHILE = {"пока", "while"}
FOR = {"для", "for"}
IN = {"в", "in"}
STEP = {"шаг", "step"}
EXCLUSIVE = {"исключительно", "exclusive"}

# Функции
FUNCTION = {"функция", "function", "func"}
RETURN = {"вернуть", "return"}

# Классы
CLASS = {"класс", "class"}
NEW = {"новый", "new"}
SELF = {"я", "self", "this"}

# Импорт
IMPORT = {"импорт", "import", "использовать"}

# Try/Catch
TRY = {"попробовать", "try"}
CATCH = {"поймать", "catch", "except"}
FINALLY = {"всегда", "finally"}
THROW = {"ошибка", "throw", "выбросить"}
WARN = {"предупреждение", "warn"}

# Pass
PASS = {"пас", "pass", "пропустить", "skip"}

# Break/Continue
BREAK = {"прервать", "break"}
CONTINUE = {"продолжить", "continue"}

# Логика
AND = {"и", "and"}
OR = {"или", "or"}
NOT = {"не", "not"}
EQ = {"равно", "eq"}
NEQ = {"не_равно", "neq"}
GT = {"больше", "gt"}
LT = {"меньше", "lt"}
GTE = {"больше_равно", "gte"}
LTE = {"меньше_равно", "lte"}

# Математика (операторы словами)
ADD = {"плюс", "add"}
SUB = {"минус", "sub"}
MUL = {"умножить", "mul"}
DIV = {"делить", "div"}
MOD = {"остаток", "mod"}

# Булевы
TRUE = {"истина", "true", "правда"}
FALSE = {"ложь", "false"}
NULL = {"ничего", "null", "none", "нет"}

# Типы
TYPE_NUM = {"число", "number", "num"}
TYPE_STR = {"строка", "string", "str"}
TYPE_BOOL = {"бул", "bool", "логическое"}
TYPE_LIST = {"список", "list"}
TYPE_DICT = {"словарь", "dict"}
TYPE_FILE = {"файл", "file"}
TYPE_ANY = {"любое", "any"}

# Цвет / стили
COLOR = {"цвет", "color"}
BG = {"фон", "background", "на"}  # "на" используется как "on"
STYLE_BOLD = {"жирный", "bold"}
STYLE_DIM = {"тусклый", "dim"}
STYLE_ITALIC = {"курсив", "italic"}
STYLE_UNDERLINE = {"подчёркнутый", "подчеркнутый", "underline"}
STYLE_BLINK = {"мигающий", "blink"}
STYLE_REVERSE = {"инверсный", "reverse"}
STYLE_STRIKE = {"зачёркнутый", "зачеркнутый", "strikethrough"}

# Ввод
INPUT = {"ввод", "input"}
STRICT = {"строго", "strict"}

# Списки — методы (используются как имя.метод)
PUSH = {"добавить", "push", "append"}
POP = {"убрать", "pop"}
SORT = {"сортировать", "sort"}
LEN = {"длина", "len"}
JOIN = {"соединить", "join"}
SPLIT = {"разбить", "split"}
REPLACE = {"заменить", "replace"}

# Все ключевые слова (для подсветки/валидации)
ALL_KEYWORDS = (
    LET | PRINT | IF | ELSE | ELIF | WHILE | FOR | IN | STEP | EXCLUSIVE |
    FUNCTION | RETURN | CLASS | NEW | SELF | IMPORT | TRY | CATCH | FINALLY |
    THROW | WARN | PASS | BREAK | CONTINUE | AND | OR | NOT | EQ | NEQ |
    GT | LT | GTE | LTE | ADD | SUB | MUL | DIV | MOD | TRUE | FALSE | NULL |
    TYPE_NUM | TYPE_STR | TYPE_BOOL | TYPE_LIST | TYPE_DICT | TYPE_FILE | TYPE_ANY |
    COLOR | BG | STYLE_BOLD | STYLE_DIM | STYLE_ITALIC | STYLE_UNDERLINE |
    STYLE_BLINK | STYLE_REVERSE | STYLE_STRIKE | INPUT | STRICT
)

STYLES = (STYLE_BOLD | STYLE_DIM | STYLE_ITALIC | STYLE_UNDERLINE |
          STYLE_BLINK | STYLE_REVERSE | STYLE_STRIKE)

TYPES = TYPE_NUM | TYPE_STR | TYPE_BOOL | TYPE_LIST | TYPE_DICT | TYPE_FILE | TYPE_ANY

def is_in(word, group):
    return word.lower() in group

def normalize_type(word):
    w = word.lower()
    if w in TYPE_NUM: return "number"
    if w in TYPE_STR: return "string"
    if w in TYPE_BOOL: return "bool"
    if w in TYPE_LIST: return "list"
    if w in TYPE_DICT: return "dict"
    if w in TYPE_FILE: return "file"
    return "any"
