import os
from dataclasses import dataclass
from pathlib import Path

from koine import winfolders


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


@dataclass(frozen=True)
class Resolucao:
    """O caminho, mais o que a concatenação teria dado.

    `concatenado` vazio significa que não houve consulta a known folder — não que
    os dois coincidiram. Quem avisa precisa dessa distinção, e é por isso que a
    divergência viaja como DADO: pôr a impressão aqui faria o `koine validar`
    herdar prosa de sessão no relatório dele.
    """
    caminho: str
    concatenado: str = ""

    @property
    def divergiu(self) -> bool:
        return bool(self.concatenado) and self.concatenado != self.caminho


def resolver_tagged_detalhado(tagged: str, *, resolver_known=None) -> Resolucao:
    """Resolve o caminho tagged, consultando a known folder do Windows quando o
    primeiro segmento é uma delas.

    Com Known Folder Move, `%USERPROFILE%` + `Documents` é casca vazia e o conteúdo
    está no OneDrive; a concatenação aponta para o lugar errado sem avisar
    (jd-task #762). Fora do Windows e para segmento que não é known folder, o
    resolvedor devolve `None` e nada muda.
    """
    if tagged.startswith("abs:"):
        return Resolucao(tagged[len("abs:"):])
    if not tagged.startswith("home:"):
        raise ValueError(f"tagged path sem prefixo home:/abs: — {tagged!r}")
    resto = tagged[len("home:"):]
    concatenado = os.path.join(str(Path.home()), resto)
    primeiro, _, cauda = resto.replace("\\", "/").partition("/")
    real = (resolver_known or winfolders.resolver)(primeiro)
    if real is None:
        return Resolucao(concatenado)
    return Resolucao(os.path.join(real, cauda) if cauda else real,
                     concatenado=concatenado)


def resolver_tagged(tagged: str) -> str:
    """Só o caminho. Os chamadores que não avisam continuam usando esta."""
    return resolver_tagged_detalhado(tagged).caminho
