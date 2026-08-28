import sys

from koine import shell
from koine.adapters import claude
from koine.contexto import ContextoMontado


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
    base = dict(usuario_path=w("u.md", "# U\nx"), koine_path=w("k.md", "# K\nx"),
                agente_path=w("hermes.md", "# H\nx"), escopo_path=w("e.md", "# E\nx"),
                indice_paths=[w("kn-indice-tecnologia.md", "# I\nx")],
                contexto_path=w("CONTEXTO.md", "# C\nx"), pasta_abs=str(tmp_path))
    base.update(kw)
    return ContextoMontado(**base)


def _sonda(mapa):
    def s(nome):
        return nome, mapa.get(nome, shell.AUSENTE)
    return s


def test_claude_desliga_o_powershell_tool_quando_a_politica_nega(tmp_path, monkeypatch):
    _isolar_home(monkeypatch, tmp_path / "home")
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(shell, "sondar", _sonda({shell.PWSH: shell.RECUSADO,
                                                 shell.POWERSHELL: shell.RECUSADO,
                                                 shell.BASH: shell.EXECUTOU}))
    lanc = claude.renderizar(_cm(tmp_path))
    assert lanc.env_vars["CLAUDE_CODE_USE_POWERSHELL_TOOL"] == "0"


def test_claude_nao_grava_a_variavel_quando_o_powershell_executa(tmp_path, monkeypatch):
    # O Koine não liga o que está desligado nem opina onde não há problema.
    _isolar_home(monkeypatch, tmp_path / "home")
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(shell, "sondar", _sonda({shell.PWSH: shell.EXECUTOU}))
    lanc = claude.renderizar(_cm(tmp_path))
    assert "CLAUDE_CODE_USE_POWERSHELL_TOOL" not in lanc.env_vars


def test_claude_fora_do_windows_nao_grava_a_variavel(tmp_path, monkeypatch):
    _isolar_home(monkeypatch, tmp_path / "home")
    monkeypatch.setattr(sys, "platform", "darwin")
    lanc = claude.renderizar(_cm(tmp_path))
    assert "CLAUDE_CODE_USE_POWERSHELL_TOOL" not in lanc.env_vars


def test_claude_mantem_a_variavel_que_ja_existia(tmp_path, monkeypatch):
    _isolar_home(monkeypatch, tmp_path / "home")
    monkeypatch.setattr(sys, "platform", "darwin")
    lanc = claude.renderizar(_cm(tmp_path))
    assert lanc.env_vars["CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD"] == "1"
