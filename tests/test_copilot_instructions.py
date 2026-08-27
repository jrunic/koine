import os

from koine.adapters import copilot
from koine.contexto import ContextoMontado

# Linhas únicas por camada: a asserção nunca é sobre cabeçalho que o próprio
# adapter escreve — com marca de template, o teste passaria com o arquivo vazio.
MARCA_USUARIO = "Linha que so existe no arquivo do usuario desta fixture."
MARCA_AGENTE = "Linha que so existe no arquivo do agente desta fixture."


def _isolar_home(monkeypatch, home):
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)


def _cm(tmp_path, **kw):
    def w(n, t):
        p = str(tmp_path / n)
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
        return p
    base = dict(usuario_path=w("u.md", f"# U\n{MARCA_USUARIO}\n"),
                koine_path=w("k.md", "# K\nx"),
                agente_path=w("hermes.md", f"# H\n{MARCA_AGENTE}\n"),
                escopo_path=w("e.md", "# E\nx"),
                indice_paths=[w("kn-indice-tecnologia.md", "# I\nx")],
                contexto_path=w("CONTEXTO.md", "# C\nx"), pasta_abs=str(tmp_path))
    base.update(kw)
    return ContextoMontado(**base)


def _instructions(lanc):
    return {p: c for p, c in lanc.arquivos_externos.items()
            if p.endswith(".instructions.md")}


def test_usuario_e_agente_vao_para_instructions(tmp_path, monkeypatch):
    """O canal COPILOT_CUSTOM_INSTRUCTIONS_DIRS entrega os *.instructions.md e
    IGNORA o AGENTS.md — medido em 27/08 com discriminante na mesma execução.
    Usuário e agente estavam no arquivo ignorado."""
    _isolar_home(monkeypatch, tmp_path / "home")
    lanc = copilot.renderizar(_cm(tmp_path))

    juntos = "\n".join(_instructions(lanc).values())
    assert MARCA_USUARIO in juntos, "o usuário não chega pelo canal que o Copilot lê"
    assert MARCA_AGENTE in juntos, "o agente não chega pelo canal que o Copilot lê"


def test_todo_instructions_tem_applyto(tmp_path, monkeypatch):
    """Sem o frontmatter `applyTo`, o arquivo não é aplicado à sessão."""
    _isolar_home(monkeypatch, tmp_path / "home")
    lanc = copilot.renderizar(_cm(tmp_path))
    instr = _instructions(lanc)
    assert instr, "nenhum .instructions.md no bundle"
    for p, c in instr.items():
        assert c.startswith('---\napplyTo:'), f"{os.path.basename(p)} sem applyTo"


def test_bootstrap_tambem_entrega_usuario_e_agente(tmp_path, monkeypatch):
    """Em bootstrap o bundle é mais magro, mas usuário e agente continuam sendo
    o que identifica a sessão — e continuam tendo que chegar pelo canal lido."""
    _isolar_home(monkeypatch, tmp_path / "home")
    lanc = copilot.renderizar(_cm(tmp_path, bootstrap=True, escopo_path="",
                                  indice_paths=[]))

    juntos = "\n".join(_instructions(lanc).values())
    assert MARCA_USUARIO in juntos
    assert MARCA_AGENTE in juntos
