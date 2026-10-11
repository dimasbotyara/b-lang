#!/usr/bin/env python3
"""Автоматически сгенерировано транспайлером b → Python."""

try:
    from rich.console import Console
    from rich.text import Text
    _b_console = Console()
    _B_HAS_RICH = True
except ImportError:
    _B_HAS_RICH = False

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
            nums = _re.findall(r"\d+", c)
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
        print("\033[" + ";".join(codes) + "m" + str(text) + "\033[0m")
    else:
        print(text)


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
        print("\033[33m⚠ Не удалось привести к " + type_ + "\033[0m", file=sys.stderr)
        return value


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
            out += "\033[38;2;{};{};{}m{}".format(r, g, b, ch)
        print(out + "\033[0m")

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


# ===== Программа =====
__b_print('Привет, мир!', fg='зелёный', bg=None, styles=['жирный'])
print('b lang работает!')
(lambda _a0: __b_rainbow(_a0))
имя = __b_coerce('программист', 'string')
__b_print(f'Привет, {имя}!', fg='золотой', bg=None, styles=[])
