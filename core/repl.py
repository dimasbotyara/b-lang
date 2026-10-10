"""Интерактивная консоль b."""
from core.lexer import tokenize
from core.parser import Parser
from core.interpreter import Interpreter
from core.errors import BError, handle_error
from core.colors import cprint

def run_repl():
    interp = Interpreter()
    buffer = []
    prompt = "b> "
    cont_prompt = ".. "

    while True:
        try:
            try:
                line = input(prompt if not buffer else cont_prompt)
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print("\n(используй 'выход' / 'exit' для выхода)")
                buffer = []
                continue

            if not buffer and line.strip() in ("выход", "exit", "quit", "q"):
                cprint("Пока! 👋 / Bye!", fg="золотой")
                break
            if not buffer and line.strip() in ("помощь", "help"):
                _print_help()
                continue
            if not buffer and line.strip() in ("очистить", "clear", "cls"):
                import os
                os.system("cls" if os.name == "nt" else "clear")
                continue

            buffer.append(line)
            # Если строка заканчивается на ':' или это блок — ждём ещё
            needs_more = _needs_continuation(buffer)
            if needs_more:
                continue

            src = "\n".join(buffer)
            buffer = []

            try:
                tokens = tokenize(src)
                ast = Parser(tokens).parse()
                interp.run(ast)
            except BError as e:
                handle_error(e)
            except Exception as e:
                from core.errors import handle_python_error
                handle_python_error(e)
        except KeyboardInterrupt:
            buffer = []
            print()

def _needs_continuation(buffer):
    """Простая проверка — нужны ли ещё строки (блок открыт)."""
    if not buffer: return False
    last = buffer[-1].rstrip()
    if not last: return False
    first_words = ["если", "if", "пока", "while", "для", "for",
                   "функция", "function", "класс", "class",
                   "попробовать", "try", "иначе", "else"]
    stripped = buffer[0].lstrip().split()
    if not stripped: return False
    if stripped[0].lower() in first_words:
        # Если последняя строка пуста — завершаем
        if len(buffer) >= 2 and buffer[-1].strip() == "":
            return False
        return True
    return False

def _print_help():
    cprint("""
🐝 b lang — помощь

Команды REPL:
  помощь / help         — эта справка
  выход / exit / quit   — выход
  очистить / clear      — очистить экран

Базовый синтаксис:
  пусть x число = 5
  печать "привет" цвет зелёный жирный
  если x больше 3
      печать "много!"
  иначе
      печать "мало"

Импорт:
  импорт рандом
  печать рандом.число 1, 100
""", fg="бирюзовый")
