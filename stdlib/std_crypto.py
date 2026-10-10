"""Модуль криптография/crypto."""
import hashlib
import secrets
import uuid as _uuid
import base64 as _b64
import urllib.parse

MODULE_NAMES = ["криптография", "crypto"]

def _hash(name):
    def _h(a):
        h = hashlib.new(name)
        h.update(str(a[0]).encode("utf-8"))
        return h.hexdigest()
    return _h

def _file_hash(a):
    h = hashlib.sha256()
    with open(a[0], "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def _verify(a):
    return hashlib.sha256(str(a[0]).encode()).hexdigest() == a[1]

def _aes_key(a):
    try:
        from cryptography.fernet import Fernet
        return Fernet.generate_key().decode()
    except ImportError:
        return "⚠ pip install cryptography"

def _aes_encrypt(a):
    try:
        from cryptography.fernet import Fernet
        f = Fernet(a[1].encode() if isinstance(a[1], str) else a[1])
        return f.encrypt(str(a[0]).encode()).decode()
    except ImportError:
        return "⚠ pip install cryptography"

def _aes_decrypt(a):
    try:
        from cryptography.fernet import Fernet
        f = Fernet(a[1].encode() if isinstance(a[1], str) else a[1])
        return f.decrypt(a[0].encode() if isinstance(a[0], str) else a[0]).decode()
    except ImportError:
        return "⚠ pip install cryptography"

FUNCTIONS = {
    "md5":    {"aliases": [], "handler": _hash("md5")},
    "sha1":   {"aliases": [], "handler": _hash("sha1")},
    "sha256": {"aliases": [], "handler": _hash("sha256")},
    "sha512": {"aliases": [], "handler": _hash("sha512")},
    "blake2": {"aliases": [], "handler": lambda a: hashlib.blake2b(str(a[0]).encode()).hexdigest()},
    "sha3":   {"aliases": [], "handler": lambda a: hashlib.sha3_256(str(a[0]).encode()).hexdigest()},
    "хеш_файла":    {"aliases": ["file_hash"],   "handler": _file_hash},
    "хеш_проверить":{"aliases": ["verify"],      "handler": _verify},
    "токен":  {"aliases": ["token"],    "handler": lambda a: secrets.token_hex(int(a[0]) if a else 16)},
    "пароль": {"aliases": ["password"], "handler": lambda a: "".join(secrets.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%") for _ in range(int(a[0]) if a else 16))},
    "соль":   {"aliases": ["salt"],     "handler": lambda a: secrets.token_bytes(int(a[0]) if a else 16).hex()},
    "ключ":   {"aliases": ["key"],      "handler": lambda a: secrets.token_bytes(int(a[0]) if a else 32).hex()},
    "uuid":   {"aliases": [],           "handler": lambda a: str(_uuid.uuid4())},
    "aes_ключ":    {"aliases": ["aes_key"],     "handler": _aes_key},
    "aes_шифр":    {"aliases": ["aes_encrypt"], "handler": _aes_encrypt},
    "aes_расшифр": {"aliases": ["aes_decrypt"], "handler": _aes_decrypt},
    "base64":      {"aliases": [],              "handler": lambda a: _b64.b64encode(str(a[0]).encode()).decode()},
    "base64_декод":{"aliases": ["base64_decode"],"handler": lambda a: _b64.b64decode(a[0]).decode()},
    "hex":         {"aliases": [],              "handler": lambda a: str(a[0]).encode().hex()},
    "hex_декод":   {"aliases": ["hex_decode"],  "handler": lambda a: bytes.fromhex(a[0]).decode()},
    "url_код":     {"aliases": ["url_encode"],  "handler": lambda a: urllib.parse.quote(str(a[0]))},
}
