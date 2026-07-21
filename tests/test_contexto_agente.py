import os

import pytest

from koine import contexto


def _seed_agente_usuario(cfg: str, slug: str) -> None:
    """Agente de usuário vive em config/agentes (onde kn-03-cria-agente grava)."""
    ag = os.path.join(cfg, "agentes")
    os.makedirs(ag, exist_ok=True)
    with open(os.path.join(ag, f"{slug}.md"), "w", encoding="utf-8") as f:
        f.write("---\ntype: agente\ntitle: X\n---\n\n# X\n")


def test_agente_usuario_resolve_do_config_ignorando_caixa(koine_home, monkeypatch):
    """Agente de usuário (config/agentes) resolve com arg de caixa divergente.

    Dois bugs travados de uma vez:
    - diretório: leia.md está em config/agentes, não em vault/agentes (que só
      tem hermes distribuído); o resolver antigo só olhava o vault e nem achava.
    - caixa: asserção na STRING do path, não em existência. APFS é
      case-insensitive e `open('Leia.md')` abriria `leia.md`, mascarando o
      defeito que quebra em FS case-sensitive (Linux/OpenClaw).
    """
    monkeypatch.setenv("HOME", koine_home["home"])
    _seed_agente_usuario(koine_home["cfg"], "leia")

    cm = contexto.resolver("Leia", koine_home["trab"])

    assert os.path.basename(cm.agente_path) == "leia.md"
    assert cm.agente_path.startswith(os.path.join(koine_home["cfg"], "agentes"))
    assert "Leia.md" not in cm.agente_path


def test_agente_inexistente_levanta_tipado_com_dados(koine_home, monkeypatch):
    """Agente ausente falha alto, tipado e com dados (arg + disponíveis) —
    cli/mensagens decidem prosa/política. Padrão ClienteNaoEncontrado. A lista
    une usuário (config) e distribuídos (vault: hermes vem do fixture real)."""
    monkeypatch.setenv("HOME", koine_home["home"])
    _seed_agente_usuario(koine_home["cfg"], "leia")

    with pytest.raises(contexto.AgenteNaoEncontrado) as ei:
        contexto.resolver("fantasma", koine_home["trab"])

    assert ei.value.agente == "fantasma"
    assert "leia" in ei.value.disponiveis
    assert "hermes" in ei.value.disponiveis
