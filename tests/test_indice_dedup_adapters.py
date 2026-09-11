"""A dedup entre domínios vale nos TRÊS caminhos de montagem.

Guarda no formato da #706: a correção que vale só onde se olhou é o defeito,
não o conserto. Aqui a asserção é sobre o que CADA caminho entrega.
"""
import pytest

from koine import adapters
from koine.contexto import ContextoMontado

IDX = """---
tipo: indice
dominio: {dom}
entradas: 1
---

## Domínio

Sinopse.
## Entradas catalogadas no escopo

- `compartilhada.md` — vale para os dois
"""


@pytest.fixture
def cm(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    refs = tmp_path / "refs"
    refs.mkdir()
    for dom in ("universal", "tecnologia"):
        (refs / f"kn-indice-{dom}.md").write_text(IDX.format(dom=dom),
                                                  encoding="utf-8")
    pasta = tmp_path / "trab"
    pasta.mkdir()
    for nome, corpo in (("usuario.md", "# Usuário"), ("KOINE.md", "# Koine"),
                        ("hermes.md", "# Hermes"), ("escopo.md", "# Escopo"),
                        ("CONTEXTO.md", "# Contexto")):
        (tmp_path / nome).write_text(corpo, encoding="utf-8")
    return ContextoMontado(
        usuario_path=str(tmp_path / "usuario.md"),
        koine_path=str(tmp_path / "KOINE.md"),
        agente_path=str(tmp_path / "hermes.md"),
        escopo_path=str(tmp_path / "escopo.md"),
        indice_paths=[str(refs / "kn-indice-universal.md"),
                      str(refs / "kn-indice-tecnologia.md")],
        contexto_path=str(tmp_path / "CONTEXTO.md"),
        pasta_abs=str(pasta),
    )


@pytest.mark.parametrize("cliente", sorted(adapters.REGISTRY))
def test_entrada_compartilhada_descrita_uma_vez_por_adapter(cliente, cm):
    lanc = adapters.get(cliente).renderizar(cm)
    todo = "\n".join(lanc.arquivos_externos.values())

    assert todo.count("— vale para os dois") == 1, (
        f"{cliente} entrega a mesma entrada descrita mais de uma vez")
    assert todo.count("`compartilhada.md`") == 2, (
        f"{cliente} perdeu a referência cruzada da entrada compartilhada")
