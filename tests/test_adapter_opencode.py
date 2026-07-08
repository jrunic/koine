import json
import os

from koine import cache
from koine.adapters import opencode
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento


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


def test_opencode_renderizar_cru(tmp_path, monkeypatch):
    _isolar_home(monkeypatch, tmp_path / "home")
    cm = _cm(tmp_path)
    lanc = opencode.renderizar(cm)
    cfg_path = cache.caminho_arquivo("opencode-configs", cache.slot_id(str(tmp_path)), "json")
    assert isinstance(lanc, Lancamento)
    assert lanc.arquivos_working_dir == {}
    assert set(lanc.arquivos_externos) == {cfg_path}
    cfg = json.loads(lanc.arquivos_externos[cfg_path])
    assert cfg["$schema"] == "https://opencode.ai/config.json"
    assert cfg["instructions"] == [cm.usuario_path, cm.agente_path, cm.escopo_path] + cm.indice_paths
    assert lanc.env_vars == {"OPENCODE_CONFIG": cfg_path, "OPENCODE_DISABLE_CLAUDE_CODE": "1"}
    assert lanc.symlinks == {os.path.join(str(tmp_path), "AGENTS.md"): cm.contexto_path}
    assert lanc.extra_args == []


def test_opencode_sem_usuario_omite_do_instructions(tmp_path, monkeypatch):
    _isolar_home(monkeypatch, tmp_path / "home")
    cm = _cm(tmp_path, usuario_path="")
    cfg = json.loads(next(iter(opencode.renderizar(cm).arquivos_externos.values())))
    assert cfg["instructions"][0] == cm.agente_path


def test_opencode_bootstrap_sem_symlink_contexto_em_instructions(tmp_path, monkeypatch):
    _isolar_home(monkeypatch, tmp_path / "home")
    cm = _cm(tmp_path, bootstrap=True, escopo_path="", indice_paths=[])
    lanc = opencode.renderizar(cm)
    cfg = json.loads(next(iter(lanc.arquivos_externos.values())))
    assert cfg["instructions"] == [cm.usuario_path, cm.agente_path, cm.contexto_path]
    assert lanc.symlinks == {}


def test_opencode_avisa_agents_md_global(tmp_path, monkeypatch, capsys):
    home = tmp_path / "home"
    os.makedirs(home / ".config" / "opencode")
    (home / ".config" / "opencode" / "AGENTS.md").write_text("global")
    _isolar_home(monkeypatch, home)
    opencode.renderizar(_cm(tmp_path))
    assert "AGENTS.md" in capsys.readouterr().err  # aviso da mescla implícita


def test_opencode_sem_global_nao_avisa(tmp_path, monkeypatch, capsys):
    _isolar_home(monkeypatch, tmp_path / "home")
    opencode.renderizar(_cm(tmp_path))
    assert capsys.readouterr().err == ""
