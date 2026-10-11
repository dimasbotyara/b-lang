#!/usr/bin/env python3
"""
b — язык программирования 🐝
Запуск: b [опции] [файл.b]
"""
import sys
import os
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

VERSION = "0.1.0"

def check_dependencies():
    """Проверка опциональных зависимостей."""
    missing = []
    optional = {
        "rich": "цветной вывод и красивые таблицы",
        "questionary": "интерактивные вопросы",
        "requests": "сетевые запросы",
        "cryptography": "AES/RSA шифрование",
    }
    for lib, desc in optional.items():
        try:
            __import__(lib)
        except ImportError:
            missing.append((lib, desc))
    return missing

def print_banner():
    try:
        from rich.console import Console
        from rich.panel import Panel
        c = Console()
        c.print(Panel.fit(
            f"[bold yellow]🐝 b lang v{VERSION}[/bold yellow]\n"
            f"[cyan]Пиши код! / Start coding![/cyan]\n"
            f"[dim]помощь / help — справка, выход / exit — выйти[/dim]",
            border_style="yellow"
        ))
    except ImportError:
        print(f"=== b lang v{VERSION} ===")
        print("Пиши код! / Start coding!")
        print("помощь / help — справка, выход / exit — выйти")

def print_help():
    print(f"""
b lang v{VERSION} 🐝

Использование:
  b <файл.b>              запустить программу
  b                       REPL (интерактивная консоль)
  b --дебаг <файл.b>      дебаг-режим
  b --debug <файл.b>      debug mode
  b --сухо <файл.b>       показать Python-код в терминале
  b --dry <файл.b>        show Python code
  b --транспилировать <файл.b>  сохранить как .py файл
  b build <файл.b>        собрать .exe (PyInstaller)
  b --проверка-кода <файл.b>    проверить синтаксис и транспайлер без запуска
  b --версия / --version  версия
  b --помощь / --help     справка
  b --проверка / --check  проверить зависимости среды
""")

def main():
    args = sys.argv[1:]

    if not args:
        from core.repl import run_repl
        print_banner()
        run_repl()
        return

    # --- Базовые команды ---
    if args[0] in ("--версия", "--version", "-v"):
        print(f"b lang v{VERSION} 🐝")
        return

    if args[0] in ("--помощь", "--help", "-h"):
        print_help()
        return

    if args[0] in ("--проверка", "--check"):
        missing = check_dependencies()
        if not missing:
            print("✅ Все зависимости установлены!")
        else:
            print("⚠ Отсутствуют (опционально):")
            for lib, desc in missing:
                print(f"  - {lib}: {desc}")
            print("\nУстановить: pip install " + " ".join(l for l, _ in missing))
        return

    # --- Команда проверки транспиляции ---
    if args[0] in ("--проверка-кода", "--check-code", "--tc"):
        if len(args) < 2:
            print("❌ Укажи файл для проверки! Пример: b --проверка-кода hello.b")
            return

        from core.lexer import tokenize
        from core.parser import Parser
        from core.transpiler import Transpiler
        from core.errors import BError, handle_error
        from core.colors import cprint

        filename = args[1]
        if not os.path.exists(filename):
            print(f"❌ Файл не найден: {filename}")
            return

        cprint(f"🔍 Анализ кода {filename}...", fg="бирюзовый", styles=["bold"])

        try:
            src = Path(filename).read_text(encoding="utf-8")

            # Шаг 1: Лексер
            cprint("  [1/3] Токенизация (Лексер)...", fg="серый")
            tokens = tokenize(src)

            # Шаг 2: Парсер
            cprint("  [2/3] Построение дерева AST (Парсер)...", fg="серый")
            ast = Parser(tokens).parse()

            # Шаг 3: Транспайлер
            cprint("  [3/3] Генерация Python-кода (Транспайлер)...", fg="серый")
            code = Transpiler().transpile(ast)

            # Всё ок!
            cprint("\n✅ Проверка пройдена! Код чистый и готов к сборке.", fg="зелёный", styles=["bold"])
            cprint(f"💡 Вес сгенерированного Python-кода: {len(code)} символов.", fg="бежевый")

        except BError as e:
            print() # отступ
            handle_error(e, filename)
        except Exception as e:
            print()
            from core.errors import handle_python_error
            handle_python_error(e, filename)
        return

    # --- Команды транспайлера ---
    if args[0] in ("--сухо", "--dry"):
        if len(args) < 2:
            print("❌ Укажи файл!")
            return
        from core.transpiler import transpile_file
        print(transpile_file(args[1]))
        return

    if args[0] in ("--транспилировать", "--transpile", "--py"):
        if len(args) < 2:
            print("❌ Укажи файл!")
            return
        from core.transpiler import transpile_to_file
        out = transpile_to_file(args[1])
        print(f"✅ Сохранено: {out}")
        return

    if args[0] == "build":
        if len(args) < 2:
            print("❌ Укажи файл!")
            return
        from core.compiler import build
        build(args[1])
        return

    # --- Дебаггер ---
    if args[0] in ("--дебаг", "--debug"):
        if len(args) < 2:
            print("❌ Укажи файл!")
            return
        from core.interpreter import Interpreter
        from core.lexer import tokenize
        from core.parser import Parser
        from core.errors import BError, handle_error
        try:
            src = Path(args[1]).read_text(encoding="utf-8")
            tokens = tokenize(src)
            ast = Parser(tokens).parse()
            Interpreter(debug=True, filename=args[1]).run(ast)
        except BError as e:
            handle_error(e, args[1])
        except KeyboardInterrupt:
            print("\n☠️  Программа прервана. / Interrupted.")
        except Exception as e:
            from core.errors import handle_python_error
            handle_python_error(e, args[1])
        return

    # --- Обычный запуск ---
    filename = args[0]
    if not os.path.exists(filename):
        print(f"❌ Файл не найден: {filename}")
        return

    from core.interpreter import Interpreter
    from core.lexer import tokenize
    from core.parser import Parser
    from core.errors import BError, handle_error

    try:
        src = Path(filename).read_text(encoding="utf-8")
        tokens = tokenize(src)
        ast = Parser(tokens).parse()
        Interpreter(filename=filename).run(ast)
    except BError as e:
        handle_error(e, filename)
    except KeyboardInterrupt:
        print("\n☠️  Программа прервана. / Interrupted.")
    except Exception as e:
        from core.errors import handle_python_error
        handle_python_error(e, filename)

if __name__ == "__main__":
    main()
