from koine._vendor import yaml


def ler(texto: str) -> tuple[dict, str]:
    """Devolve (frontmatter_dict, corpo). Sem frontmatter → ({}, texto)."""
    if not texto.startswith("---"):
        return {}, texto
    # separa o bloco --- ... --- inicial do corpo
    partes = texto.split("\n", 1)
    resto = partes[1] if len(partes) > 1 else ""
    fim = resto.find("\n---")
    if fim == -1:
        return {}, texto
    bloco = resto[:fim]
    corpo = resto[fim + len("\n---"):].lstrip("\n")
    dados = yaml.safe_load(bloco) or {}
    return dados, corpo
