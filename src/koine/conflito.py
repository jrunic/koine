import os

from koine import escrita

# A política mora em `escrita.py` — este módulo é a porta do `conflito.go` e
# delega. Os nomes seguem exportados: são consumidos por `cli.py` e pelos testes.
MARCADOR_KOINE = escrita.MARCADOR_KOINE
_ASSINATURA_RETROCOMPAT = escrita.ASSINATURA_RETROCOMPAT
ConflitoErro = escrita.ConflitoErro


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
    # arquivo regular no caminho do symlink: sai mesmo sendo nosso — o lugar
    # tem que ficar livre para o os.symlink
    escrita.preservar(link, apenas_do_usuario=False)


def resolver_arquivo_conflito(p: str) -> None:
    """Porta integral do ramo arquivo de cmd/kn-agente/conflito.go
    (resolverArquivoConflito + temMarkerKoine + fazerBackupComAviso).
    Path que será escrito como arquivo regular. Não existe → OK; symlink →
    ConflitoErro (escrever "atravessaria" o symlink — perda de dado);
    diretório → ConflitoErro; arquivo com marcador Koine (ou assinatura
    retrocompat) → OK (regeneração idempotente); arquivo sem marcador →
    backup .bak livre + aviso stderr e prossegue. Nunca remove sem backup."""
    escrita.preservar(p)


