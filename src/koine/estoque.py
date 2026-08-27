# src/koine/estoque.py
"""O que o mecanismo antigo deixou na pasta do usuário, e o que pode sair.

Esta é a única operação do Koine que **remove** arquivo da pasta — e remoção,
diferente de sobrescrita, não deixa `.bak` por definição. Por isso a pergunta é
respondida aqui, sozinha, e por evidência: o marcador da primeira linha é a
única prova de propriedade que existe.
"""
import os

from koine import escrita


def removivel(p: str) -> bool:
    """O arquivo em `p` é estoque do mecanismo antigo, e pode sair?

    Três respostas, e só a primeira remove:

    - nosso, sem a marca de "a pedido" → estoque; sai;
    - nosso, com a marca → o usuário mandou gerar, e no modo skills a pasta é a
      **única** via de entrega. Fica;
    - do usuário → nunca sai.
    """
    if not os.path.isfile(p) or os.path.islink(p):
        return False
    if not escrita.e_nosso(p):
        return False
    return not escrita.tem_marca_a_pedido(p)
