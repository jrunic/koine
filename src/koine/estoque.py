# src/koine/estoque.py
"""O que o mecanismo antigo deixou na pasta do usuário, e o que pode sair.

Esta é a única operação do Koine que **remove** arquivo da pasta — e remoção,
diferente de sobrescrita, não deixa `.bak` por definição. Por isso a pergunta é
respondida aqui, sozinha, e por evidência: o marcador da primeira linha é a
única prova de propriedade que existe.
"""
import os

from koine import adapters, escrita

# Os nomes que o mecanismo antigo materializava na pasta. A limpeza só olha para
# eles: um arquivo com o nosso marcador em OUTRO nome (uma cópia que o usuário
# fez, por exemplo) não é estoque nosso, e remoção não deixa .bak.
NOMES = sorted({m.ARQUIVO for m in adapters.REGISTRY.values()})


def removivel(p: str) -> bool:
    """O arquivo em `p` é estoque do mecanismo antigo, e pode sair?

    Três respostas, e só a primeira remove:

    - nosso, sem a marca de "a pedido" → estoque; sai;
    - nosso, com a marca → o usuário mandou gerar, e a pasta é a
      **única** via de entrega. Fica;
    - do usuário → nunca sai.
    """
    if not os.path.isfile(p) or os.path.islink(p):
        return False
    if not escrita.e_nosso(p):
        return False
    return not escrita.tem_marca_a_pedido(p)


def removivel_symlink(link: str, pasta: str) -> bool:
    """O symlink em `link` é um dos dois que o Koine criava?

    Caminho **E** alvo: casar só pelo alvo removeria qualquer atalho do usuário
    apontando para o `CONTEXTO.md` — um `notas.md`, um `README.md` —, e remoção
    não deixa `.bak`. Casar só pelo caminho removeria um `AGENTS.md` do usuário
    apontando para outro lugar.

    Caso que a regra reconhecidamente não separa: um `AGENTS.md` que o próprio
    usuário tenha apontado para o `CONTEXTO.md` desta pasta. É indistinguível do
    nosso, e o dano é um symlink recriável com o alvo intacto.
    """
    if not os.path.islink(link):
        return False
    if os.path.relpath(link, pasta) not in NOMES:
        return False
    alvo = os.readlink(link)
    if not os.path.isabs(alvo):
        alvo = os.path.join(os.path.dirname(link), alvo)
    return os.path.realpath(alvo) == os.path.realpath(
        os.path.join(pasta, "CONTEXTO.md"))


def limpar(pasta: str) -> list:
    """Remove o estoque do mecanismo antigo desta pasta. Devolve o que saiu.

    Oportunista, por pasta, no launch: não há varredura global. Pasta que o
    usuário nunca mais abrir pelo Koine mantém o arquivo antigo — consequência
    declarada na spec.
    """
    saiu = []
    for nome in NOMES:
        p = os.path.join(pasta, nome)
        if removivel_symlink(p, pasta) or removivel(p):
            os.remove(p)
            saiu.append(p)
    return saiu
