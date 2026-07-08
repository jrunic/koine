import os
import sys


class ConflitoErro(Exception):
    """Estado ambíguo pré-existente no path a materializar; resolução manual."""


def resolver_symlink_conflito(link: str, alvo_esperado: str) -> None:
    """Porta do ramo symlink de cmd/kn-agente/conflito.go (resolverSymlinkConflito).
    Regras: não existe → OK; symlink com alvo correto → no-op; symlink com alvo
    divergente → ConflitoErro; diretório → ConflitoErro; arquivo regular →
    backup .bak livre + aviso em stderr e prossegue. Nunca remove sem backup."""
    if not os.path.lexists(link):
        return
    if os.path.islink(link):
        atual = os.readlink(link)
        if atual == alvo_esperado:
            return
        raise ConflitoErro(
            f"conflito em {link}: symlink aponta para {atual!r}, esperado "
            f"{alvo_esperado!r} — resolva manualmente")
    if os.path.isdir(link):
        raise ConflitoErro(f"conflito em {link}: é um diretório — resolva manualmente")
    _backup_com_aviso(link)


def _backup_com_aviso(p: str) -> None:
    bak = _backup_livre(p)
    os.rename(p, bak)
    print(f"aviso: {os.path.basename(p)} existente (não gerado pelo Koine) salvo como "
          f"{os.path.basename(bak)} — gerando contexto da sessão", file=sys.stderr)


def _backup_livre(p: str) -> str:
    if not os.path.lexists(p + ".bak"):
        return p + ".bak"
    i = 1
    while os.path.lexists(f"{p}.bak.{i}"):
        i += 1
    return f"{p}.bak.{i}"
