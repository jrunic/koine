# src/koine/dircopy.py
"""Comparar duas árvores de diretório e trocar o destino pela origem sem
deixar resíduo — extraído de `skills.py` porque a distribuição de skill de
usuário (`habilidade_usuario.py`) precisa da mesma lógica que a distribuição
do vault, e duplicá-la arriscaria as duas divergirem.
"""
import os
import shutil


def arvore(base: str) -> dict:
    out = {}
    for raiz, _, arqs in os.walk(base):
        for a in arqs:
            p = os.path.join(raiz, a)
            with open(p, "rb") as f:
                out[os.path.relpath(p, base)] = f.read()
    return out


def trocar_dir(src: str, dst: str) -> None:
    """Monta a árvore nova ao lado e troca no fim.

    O nome temporário começa com ponto de propósito: não casa o filtro `kn-*`
    do instalador de skills do vault, então nem ele nem o cliente o enxergam
    como skill enquanto existe.
    """
    pai = os.path.dirname(dst)
    tmp = os.path.join(pai, "." + os.path.basename(dst) + ".koine-novo")
    if os.path.lexists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp)
    shutil.rmtree(dst)
    os.replace(tmp, dst)
