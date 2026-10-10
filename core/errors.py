"""Система ошибок b с мотивационными речами."""
from pathlib import Path
from motivations import get_motivation, detect_lang

class BError(Exception):
    def __init__(self, message, line=None, hint=None, code=None):
        self.message = message
        self.line = line
        self.hint = hint
        self.code = code
        super().__init__(message)

class BSyntaxError(BError): pass
class BRuntimeError(BError): pass
class BTypeError(BError): pass
class BNameError(BError): pass
class BImportError(BError): pass

def _detect_file_lang(filename):
    try:
        src = Path(filename).read_text(encoding="utf-8")
        return detect_lang(src)
    except Exception:
        return "ru"

def handle_error(err: BError, filename=None):
    from core.colors import cprint
    lang = _detect_file_lang(filename) if filename else "ru"

    # Ошибка — коралловый
    header = f"❌ Ошибка" if lang == "ru" else "❌ Error"
    if err.line:
        header += f" (строка {err.line})" if lang == "ru" else f" (line {err.line})"
    cprint(f"{header}: {err.message}", fg="коралловый", styles=["bold"])

    if err.code:
        cprint(f"   → {err.code}", fg="серый", styles=["dim"])

    if err.hint:
        hint_label = "💡 Подсказка" if lang == "ru" else "💡 Hint"
        cprint(f"{hint_label}: {err.hint}", fg="бирюзовый")

    # Мотивация
    cprint(f"\n{get_motivation(lang)}", fg="золотой", styles=["italic"])

def handle_warning(message, line=None, hint=None, lang="ru"):
    from core.colors import cprint
    header = "⚠ Предупреждение" if lang == "ru" else "⚠ Warning"
    if line:
        header += f" (строка {line})" if lang == "ru" else f" (line {line})"
    cprint(f"{header}: {message}", fg="янтарный", styles=["bold"])
    if hint:
        hint_label = "💡 Подсказка" if lang == "ru" else "💡 Hint"
        cprint(f"{hint_label}: {hint}", fg="бирюзовый")

def handle_python_error(err, filename=None):
    from core.colors import cprint
    lang = _detect_file_lang(filename) if filename else "ru"
    cprint(f"❌ Внутренняя ошибка: {type(err).__name__}: {err}",
           fg="коралловый", styles=["bold"])
    import traceback
    cprint(traceback.format_exc(), fg="серый", styles=["dim"])
    cprint(f"\n{get_motivation(lang)}", fg="золотой", styles=["italic"])
