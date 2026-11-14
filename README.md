# 🐝 b-lang

**b** — a programming language with a bee soul, implemented in Python. Keywords work in both Russian and English, output can be colored right from the language, and programs can be transpiled to Python.

```b
// Привет мир на b! 🐝
печать "Привет, мир!" цвет зелёный жирный
печать цвет.радуга "b lang работает!"

пусть имя строка = "программист"
печать "Привет, {имя}!" цвет золотой
```

The same in English: `let`, `print`, `if`/`else`, `function`, `class` — pick your side.

## Features

- **Interpreter + REPL** — lexer, parser, interpreter, friendly errors
- **Transpiler to Python** — `examples/hello.py` is generated from `hello.b`
- **Bilingual keywords** — `пусть`/`let`, `печать`/`print`, `пока`/`while`, `функция`/`func`…
- **Inline colored output** — `цвет зелёный жирный`, `цвет.радуга`
- **String interpolation** — `"Привет, {имя}!"`
- **Stdlib** — math, text, time, file, net, random, ask, rich, crypto, sys
- **Optional extensions** — rich (pretty output), questionary (interactive prompts), requests, cryptography (AES/RSA)

## Quick start

```bash
python b.py examples/hello.b     # run a program
python b.py                      # REPL
```

More programs live in [`b-lang-more-examples`](https://github.com/dimasbotyara/b-lang-more-examples).

## License

MIT
