# src/koine/escrita.py
"""Quem pode escrever na pasta do usuário, e o que acontece com o que já está lá.

Dona única de três perguntas que viviam espalhadas: *isto é meu?*, *posso
escrever aqui?* e *como escrever sem perder nada*. Antes elas existiam no
`conflito.py` — porta do `conflito.go`, consumida só pelo launch — e o `gerar`
escrevia direto, sem nenhuma delas: em 27/08/2026 um `CLAUDE.md` pessoal foi
substituído sem `.bak`, e o comando ainda imprimiu "Escrito ... bytes".

Duas superfícies gravam o mesmo recurso; a política é uma só.
"""
import os
import sys

from koine import backup as _backup_mod

MARCADOR_KOINE = "<!-- gerado por kn-agente -->"
# Retrocompatibilidade: CLAUDE.md/GEMINI.md gerados pré-Fase-3 do Go não têm o
# marcador HTML, mas carregam a assinatura do template (conflito.go:139-140).
ASSINATURA_RETROCOMPAT = "Regerar: `kn-agente"


class ConflitoErro(Exception):
    """Estado ambíguo pré-existente no path a materializar; resolução manual."""


def e_nosso(p: str) -> bool:
    """O arquivo em `p` foi gerado pelo Koine?

    Erro de leitura ou de decodificação → False: o arquivo é tratado como do
    usuário e cai no backup, nunca na sobrescrita (mesma semântica do
    `err != nil → false` do Go).
    """
    try:
        with open(p, encoding="utf-8") as f:
            s = f.read()
    except (OSError, UnicodeDecodeError):
        return False
    if s.split("\n", 1)[0] == MARCADOR_KOINE:
        return True
    return ASSINATURA_RETROCOMPAT in s


def preservar(p: str, apenas_do_usuario: bool = True) -> None:
    """Guarda em `.bak` livre o que estiver em `p`, liberando o caminho.

    Não existe → no-op. Symlink ou diretório → ConflitoErro: escrever
    atravessaria o symlink e destruiria o alvo.

    `apenas_do_usuario=True` (default) pula o que é nosso: quem vai ocupar o
    lugar é outro arquivo regular, a sobrescrita basta, e fazer `.bak` de
    regeneração idempotente encheria a pasta. `False` é para quem vai pôr um
    SYMLINK no lugar — arquivo nosso também precisa sair, porque `os.symlink`
    sobre caminho ocupado estoura. É o cruzamento codex→opencode.
    """
    if not os.path.lexists(p):
        return
    if os.path.islink(p):
        raise ConflitoErro(
            f"conflito em {p}: é um symlink — esperava arquivo regular; "
            "resolva manualmente")
    if os.path.isdir(p):
        raise ConflitoErro(f"conflito em {p}: é um diretório — resolva manualmente")
    if apenas_do_usuario and e_nosso(p):
        return
    bak = _backup_mod.caminho_livre(p + ".bak")
    os.rename(p, bak)
    if not e_nosso(p):
        print(f"aviso: {os.path.basename(p)} existente (não gerado pelo Koine) "
              f"salvo como {os.path.basename(bak)} — gerando contexto da sessão",
              file=sys.stderr)


def gravar(p: str, conteudo: str) -> None:
    """Preserva o que houver e grava `conteudo` em `p`.

    A gravação é por temporário + troca atômica: o arquivo que o cliente vai ler
    nunca existe pela metade, e uma escrita interrompida não deixa resíduo
    visível na pasta de trabalho — o temporário nasce oculto e some no `finally`.
    """
    preservar(p)
    d = os.path.dirname(p) or "."
    tmp = os.path.join(d, f".{os.path.basename(p)}.koine-tmp")
    tmp = _backup_mod.caminho_livre(tmp)
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(conteudo)
        os.replace(tmp, p)
    finally:
        if os.path.lexists(tmp):
            os.remove(tmp)
