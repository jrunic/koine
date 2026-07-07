import os
from pathlib import Path


def _xdg(env: str, *fallback: str) -> str:
    v = os.environ.get(env)
    if v:
        return os.path.join(v, "koine")
    return os.path.join(str(Path.home()), *fallback, "koine")


def vault_dir() -> str:
    return _xdg("XDG_DATA_HOME", ".local", "share")


def config_dir() -> str:
    return _xdg("XDG_CONFIG_HOME", ".config")


def cache_dir() -> str:
    return _xdg("XDG_CACHE_HOME", ".cache")


def resolver_tagged(tagged: str) -> str:
    if tagged.startswith("home:"):
        return os.path.join(str(Path.home()), tagged[len("home:"):])
    if tagged.startswith("abs:"):
        return tagged[len("abs:"):]
    raise ValueError(f"tagged path sem prefixo home:/abs: — {tagged!r}")
