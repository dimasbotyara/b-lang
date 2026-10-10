"""Сборка .exe через PyInstaller — используем настоящий транспайлер."""
import os
import sys
import subprocess
from pathlib import Path

def build(filename, keep_py=False):
    """
    Собирает .b файл в .exe:
      1. Транспилирует b → Python
      2. Запускает PyInstaller
    """
    from core.transpiler import transpile_file
    from core.colors import cprint

    src = Path(filename).resolve()
    if not src.exists():
        cprint(f"❌ Файл не найден: {filename}", fg="коралловый")
        return

    name = src.stem
    cprint(f"🔨 Сборка {name}...", fg="бирюзовый", styles=["bold"])

    # 1. Транспиляция
    cprint("📦 Транспиляция b → Python...", fg="серый")
    try:
        py_code = transpile_file(str(src))
    except Exception as e:
        cprint(f"❌ Ошибка транспиляции: {e}", fg="коралловый")
        import traceback
        cprint(traceback.format_exc(), fg="серый", styles=["dim"])
        return

    py_path = src.with_suffix(".py")
    py_path.write_text(py_code, encoding="utf-8")
    cprint(f"   → {py_path.name}", fg="зелёный")

    # 2. Проверка PyInstaller
    try:
        import PyInstaller
    except ImportError:
        cprint("❌ Нужен PyInstaller: pip install pyinstaller", fg="коралловый")
        cprint(f"💡 Python-файл сохранён: {py_path}", fg="бирюзовый")
        return

    # 3. Сборка
    cprint("📦 PyInstaller...", fg="серый")
    try:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", name,
            "--distpath", str(src.parent / "dist"),
            "--workpath", str(src.parent / "build"),
            "--specpath", str(src.parent),
            "--clean",
            str(py_path)
        ], capture_output=True, text=True)

        if result.returncode != 0:
            cprint("❌ PyInstaller упал:", fg="коралловый")
            cprint(result.stderr[-1000:], fg="серый", styles=["dim"])
            return

        exe_name = name + (".exe" if os.name == "nt" else "")
        exe_path = src.parent / "dist" / exe_name
        cprint(f"✅ Готово: {exe_path}", fg="зелёный", styles=["bold"])
    finally:
        # Чистим промежуточные файлы
        if not keep_py:
            try: py_path.unlink()
            except: pass
        try:
            (src.parent / f"{name}.spec").unlink()
        except: pass
