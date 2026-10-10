"""Цветной вывод с поддержкой truecolor, палитры, градиентов."""
import re

# Палитра (имя → hex)
PALETTE = {
    # базовые
    "красный": "#FF0000", "red": "#FF0000",
    "зелёный": "#00FF00", "зеленый": "#00FF00", "green": "#00FF00",
    "синий": "#0000FF", "blue": "#0000FF",
    "жёлтый": "#FFFF00", "желтый": "#FFFF00", "yellow": "#FFFF00",
    "голубой": "#00FFFF", "cyan": "#00FFFF",
    "белый": "#FFFFFF", "white": "#FFFFFF",
    "чёрный": "#000000", "черный": "#000000", "black": "#000000",
    "фиолетовый": "#8000FF", "magenta": "#FF00FF",
    # палитра
    "розовый": "#FFC0CB", "pink": "#FFC0CB",
    "пурпурный": "#800080", "purple": "#800080",
    "лиловый": "#EE82EE", "violet": "#EE82EE",
    "бирюзовый": "#40E0D0", "turquoise": "#40E0D0",
    "изумрудный": "#50C878", "emerald": "#50C878",
    "лаймовый": "#CCFF00", "lime": "#CCFF00",
    "оливковый": "#808000", "olive": "#808000",
    "бежевый": "#F5F5DC", "beige": "#F5F5DC",
    "коричневый": "#8B4513", "brown": "#8B4513",
    "серый": "#808080", "gray": "#808080", "grey": "#808080",
    "оранжевый": "#FFA500", "orange": "#FFA500",
    "тёмно_оранжевый": "#FF8C00", "темно_оранжевый": "#FF8C00", "dark_orange": "#FF8C00",
    "коралловый": "#FF7F50", "coral": "#FF7F50",
    "мандарин": "#FF8243", "mandarin": "#FF8243",
    "янтарь": "#FFBF00", "янтарный": "#FFBF00", "amber": "#FFBF00",
    "золотой": "#FFD700", "gold": "#FFD700",
}

STYLE_MAP = {
    "жирный": "bold", "bold": "bold",
    "тусклый": "dim", "dim": "dim",
    "курсив": "italic", "italic": "italic",
    "подчёркнутый": "underline", "подчеркнутый": "underline", "underline": "underline",
    "мигающий": "blink", "blink": "blink",
    "инверсный": "reverse", "reverse": "reverse",
    "скрытый": "conceal", "hidden": "conceal",
    "зачёркнутый": "strike", "зачеркнутый": "strike", "strikethrough": "strike",
}

def resolve_color(name):
    """Преобразует имя цвета/hex/rgb в hex."""
    if not name:
        return None
    name = str(name).strip()
    if name.startswith("#"):
        return name
    if name.startswith("rgb"):
        nums = re.findall(r"\d+", name)
        if len(nums) >= 3:
            r, g, b = int(nums[0]), int(nums[1]), int(nums[2])
            return f"#{r:02X}{g:02X}{b:02X}"
    return PALETTE.get(name.lower())

def build_rich_style(fg=None, bg=None, styles=None):
    """Собирает rich-style строку."""
    parts = []
    if styles:
        for s in styles:
            m = STYLE_MAP.get(s.lower() if isinstance(s, str) else s)
            if m:
                parts.append(m)
    if fg:
        c = resolve_color(fg)
        if c:
            parts.append(c)
    if bg:
        c = resolve_color(bg)
        if c:
            parts.append(f"on {c}")
    return " ".join(parts)

def cprint(text, fg=None, bg=None, styles=None):
    """Печать с цветом (через rich, с fallback)."""
    try:
        from rich.console import Console
        c = Console()
        style = build_rich_style(fg, bg, styles)
        if style:
            c.print(text, style=style)
        else:
            c.print(text)
    except ImportError:
        # ANSI fallback
        _ansi_print(text, fg, bg, styles)

def _ansi_print(text, fg=None, bg=None, styles=None):
    """Fallback без rich — через ANSI escape."""
    codes = []
    style_codes = {"bold":"1","dim":"2","italic":"3","underline":"4",
                   "blink":"5","reverse":"7","strike":"9"}
    if styles:
        for s in styles:
            m = STYLE_MAP.get(s.lower() if isinstance(s, str) else s)
            if m and m in style_codes:
                codes.append(style_codes[m])
    if fg:
        hex_c = resolve_color(fg)
        if hex_c:
            r, g, b = int(hex_c[1:3],16), int(hex_c[3:5],16), int(hex_c[5:7],16)
            codes.append(f"38;2;{r};{g};{b}")
    if bg:
        hex_c = resolve_color(bg)
        if hex_c:
            r, g, b = int(hex_c[1:3],16), int(hex_c[3:5],16), int(hex_c[5:7],16)
            codes.append(f"48;2;{r};{g};{b}")
    if codes:
        print(f"\033[{';'.join(codes)}m{text}\033[0m")
    else:
        print(text)

def rainbow(text):
    """Радуга 🌈"""
    colors = ["#FF0000", "#FF8800", "#FFFF00", "#00FF00",
              "#00FFFF", "#0088FF", "#8800FF"]
    try:
        from rich.console import Console
        from rich.text import Text
        t = Text()
        for i, ch in enumerate(str(text)):
            t.append(ch, style=colors[i % len(colors)])
        Console().print(t)
    except ImportError:
        for i, ch in enumerate(str(text)):
            hex_c = colors[i % len(colors)]
            r,g,b = int(hex_c[1:3],16), int(hex_c[3:5],16), int(hex_c[5:7],16)
            print(f"\033[38;2;{r};{g};{b}m{ch}", end="")
        print("\033[0m")
    return None  # явно возвращаем None

def fire(text):
    """Огонь 🔥 (перелив от желтого к красному)"""
    colors = ["#FFFF00", "#FFAA00", "#FF6600", "#FF3300", "#CC0000"]
    s = str(text)
    try:
        from rich.text import Text
        from rich.console import Console
        t = Text()
        n = max(1, len(s) - 1)
        for i, ch in enumerate(s):
            idx = int(i / n * (len(colors) - 1))
            t.append(ch, style=colors[idx])
        Console().print(t)
    except ImportError:
        # Красивый ANSI Fallback для огня
        n = max(1, len(s) - 1)
        for i, ch in enumerate(s):
            idx = int(i / n * (len(colors) - 1))
            hex_c = colors[idx]
            r, g, b = int(hex_c[1:3], 16), int(hex_c[3:5], 16), int(hex_c[5:7], 16)
            print(f"\033[38;2;{r};{g};{b}m{ch}", end="")
        print("\033[0m")
    return None


def gradient(text, c1, c2):
    """Градиент от цвета c1 к цвету c2 🌊"""
    c1_hex = resolve_color(c1) or "#FFFFFF"
    c2_hex = resolve_color(c2) or "#000000"

    r1, g1, b1 = int(c1_hex[1:3], 16), int(c1_hex[3:5], 16), int(c1_hex[5:7], 16)
    r2, g2, b2 = int(c2_hex[1:3], 16), int(c2_hex[3:5], 16), int(c2_hex[5:7], 16)

    s = str(text)
    n = max(1, len(s) - 1)

    try:
        from rich.text import Text
        from rich.console import Console
        t = Text()
        for i, ch in enumerate(s):
            r = int(r1 + (r2 - r1) * i / n)
            g = int(g1 + (g2 - g1) * i / n)
            b = int(b1 + (b2 - b1) * i / n)
            t.append(ch, style=f"#{r:02X}{g:02X}{b:02X}")
        Console().print(t)
    except ImportError:
        # Красивый ANSI Fallback для градиента
        for i, ch in enumerate(s):
            r = int(r1 + (r2 - r1) * i / n)
            g = int(g1 + (g2 - g1) * i / n)
            b = int(b1 + (b2 - b1) * i / n)
            print(f"\033[38;2;{r};{g};{b}m{ch}", end="")
        print("\033[0m")
    return None

def mix(c1, c2):
    """Смешать два цвета."""
    c1 = resolve_color(c1) or "#000000"
    c2 = resolve_color(c2) or "#000000"
    r = (int(c1[1:3],16) + int(c2[1:3],16)) // 2
    g = (int(c1[3:5],16) + int(c2[3:5],16)) // 2
    b = (int(c1[5:7],16) + int(c2[5:7],16)) // 2
    return f"#{r:02X}{g:02X}{b:02X}"

def show_palette():
    """Показать всю встроенную палитру b lang 🎨"""
    try:
        from rich.table import Table
        from rich.console import Console
        c = Console()
        t = Table(title="🎨 Палитра b lang", border_style="cyan")
        t.add_column("Имя / Name", style="bold")
        t.add_column("Hex")
        t.add_column("Пример / Preview")
        seen = set()
        for name, hex_c in PALETTE.items():
            if hex_c in seen:
                continue
            seen.add(hex_c)
            t.add_row(name, hex_c, f"[{hex_c}]██████████[/{hex_c}]")
        c.print(t)
    except ImportError:
        # ANSI Fallback для палитры (рисуем цветные блоки символами)
        print("=== 🎨 Палитра b lang ===")
        seen = set()
        for name, hex_c in PALETTE.items():
            if hex_c in seen:
                continue
            seen.add(hex_c)
            r, g, b = int(hex_c[1:3], 16), int(hex_c[3:5], 16), int(hex_c[5:7], 16)
            # Выводим имя цвета и цветной блок █ через ANSI escape-коды
            print(f"  {name:<16} {hex_c} \033[38;2;{r};{g};{b}m██████████\033[0m")
    return None
