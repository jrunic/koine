import os
import sys


MARCADOR_KOINE = "<!-- gerado por kn-agente -->"
# retrocompatibilidade: CLAUDE.md/GEMINI.md gerados pré-Fase-3 do Go não têm o
# marcador HTML, mas carregam a assinatura do template (conflito.go:139-140)
_ASSINATURA_RETROCOMPAT = "Regerar: `kn-agente"


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


def resolver_arquivo_conflito(p: str) -> None:
    """Porta integral do ramo arquivo de cmd/kn-agente/conflito.go
    (resolverArquivoConflito + temMarkerKoine + fazerBackupComAviso).
    Path que será escrito como arquivo regular. Não existe → OK; symlink →
    ConflitoErro (escrever "atravessaria" o symlink — perda de dado);
    diretório → ConflitoErro; arquivo com marcador Koine (ou assinatura
    retrocompat) → OK (regeneração idempotente); arquivo sem marcador →
    backup .bak livre + aviso stderr e prossegue. Nunca remove sem backup."""
    if not os.path.lexists(p):
        return
    if os.path.islink(p):
        raise ConflitoErro(
            f"conflito em {p}: é um symlink — esperava arquivo regular; resolva manualmente")
    if os.path.isdir(p):
        raise ConflitoErro(f"conflito em {p}: é um diretório — resolva manualmente")
    if _tem_marcador_koine(p):
        return  # regeneração idempotente
    _backup_com_aviso(p)  # arquivo do usuário → preserva em .bak e prossegue


def _tem_marcador_koine(p: str) -> bool:
    """Porta de temMarkerKoine (conflito.go:129-141). Erro de leitura ou de
    decodificação → False: arquivo tratado como do usuário — cai no backup,
    nunca sobrescreve (mesma semântica do `err != nil → false` do Go).

    Duas divergências micro DECLARADAS vs Go, ambas benignas:
    (a) arquivo com bytes inválidos UTF-8 contendo a assinatura retrocompat →
        Python retorna False e faz backup (mais seguro); o Go (bytes.Contains,
        sem decode) sobrescreveria;
    (b) 1ª linha com CRLF → Python casa o marcador na 1ª linha (universal
        newlines removem o \\r); o Go só o encontraria pelo ramo Contains."""
    try:
        with open(p, encoding="utf-8") as f:
            s = f.read()
    except (OSError, UnicodeDecodeError):
        return False
    if s.split("\n", 1)[0] == MARCADOR_KOINE:
        return True
    return _ASSINATURA_RETROCOMPAT in s


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
