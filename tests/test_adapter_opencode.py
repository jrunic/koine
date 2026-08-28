import json
import os
import sys

from koine import cache, shell
from koine.adapters import opencode
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento


def _isolar_home(monkeypatch, home):
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)


def _sonda(mapa):
    def s(nome):
        return nome, mapa.get(nome, shell.AUSENTE)
    return s


def _forcar_sonda(monkeypatch, mapa):
    """A sonda real executa processos; nos testes ela é injetada pelo módulo."""
    monkeypatch.setattr(shell, "sondar", _sonda(mapa))


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
    assert cfg["instructions"] == ([cm.usuario_path, cm.koine_path, cm.agente_path,
                                    cm.escopo_path] + cm.indice_paths + [cm.contexto_path])
    assert lanc.env_vars == {"OPENCODE_CONFIG": cfg_path, "OPENCODE_DISABLE_CLAUDE_CODE": "1"}
    # o CONTEXTO.md chega por REFERÊNCIA no `instructions`; o symlink na pasta
    # do usuário some junto com todo arquivo gerado ali
    assert lanc.symlinks == {}
    assert lanc.extra_args == []


def test_opencode_sem_usuario_omite_do_instructions(tmp_path, monkeypatch):
    _isolar_home(monkeypatch, tmp_path / "home")
    cm = _cm(tmp_path, usuario_path="")
    cfg = json.loads(next(iter(opencode.renderizar(cm).arquivos_externos.values())))
    assert cfg["instructions"][0] == cm.koine_path


def test_opencode_bootstrap_contexto_em_instructions(tmp_path, monkeypatch):
    _isolar_home(monkeypatch, tmp_path / "home")
    cm = _cm(tmp_path, bootstrap=True, escopo_path="", indice_paths=[])
    lanc = opencode.renderizar(cm)
    cfg = json.loads(next(iter(lanc.arquivos_externos.values())))
    assert cfg["instructions"] == [cm.usuario_path, cm.koine_path, cm.agente_path,
                                   cm.contexto_path]
    assert lanc.symlinks == {}


def test_opencode_windows_usa_o_melhor_degrau_disponivel(tmp_path, monkeypatch):
    # máquina Windows comum: o pwsh roda, e é o que o usuário deve receber.
    _isolar_home(monkeypatch, tmp_path / "home")
    monkeypatch.setattr(sys, "platform", "win32")
    _forcar_sonda(monkeypatch, {shell.PWSH: shell.EXECUTOU, shell.CMD: shell.EXECUTOU})
    cfg = json.loads(next(iter(opencode.renderizar(_cm(tmp_path)).arquivos_externos.values())))
    assert cfg["shell"] == "pwsh"


def test_opencode_windows_cai_no_bash_quando_a_politica_nega_o_powershell(tmp_path, monkeypatch):
    # é a estação corporativa medida em 28/08: pwsh e powershell recusados (1260),
    # Git Bash presente. Antes desta mudança ela recebia cmd.
    _isolar_home(monkeypatch, tmp_path / "home")
    monkeypatch.setattr(sys, "platform", "win32")
    _forcar_sonda(monkeypatch, {shell.PWSH: shell.RECUSADO,
                                shell.POWERSHELL: shell.RECUSADO,
                                shell.BASH: shell.EXECUTOU,
                                shell.CMD: shell.EXECUTOU})
    cfg = json.loads(next(iter(opencode.renderizar(_cm(tmp_path)).arquivos_externos.values())))
    assert cfg["shell"] == "bash"


def test_opencode_windows_chega_no_cmd_quando_e_o_unico(tmp_path, monkeypatch):
    # o piso: estação travada e SEM Git Bash. Nenhuma máquina Windows pode ficar
    # sem shell — é a correção da v0.5.3, que esta mudança não pode regredir.
    _isolar_home(monkeypatch, tmp_path / "home")
    monkeypatch.setattr(sys, "platform", "win32")
    _forcar_sonda(monkeypatch, {shell.PWSH: shell.RECUSADO,
                                shell.POWERSHELL: shell.RECUSADO,
                                shell.BASH: shell.AUSENTE,
                                shell.CMD: shell.EXECUTOU})
    cfg = json.loads(next(iter(opencode.renderizar(_cm(tmp_path)).arquivos_externos.values())))
    assert cfg["shell"] == "cmd"


def test_opencode_windows_grava_caminho_absoluto_quando_o_bash_esta_fora_do_path(tmp_path, monkeypatch):
    _isolar_home(monkeypatch, tmp_path / "home")
    monkeypatch.setattr(sys, "platform", "win32")
    absoluto = r"C:\Users\x\AppData\Local\Programs\Git\bin\bash.exe"
    monkeypatch.setattr(shell, "sondar",
                        lambda n: (absoluto, shell.EXECUTOU) if n == shell.BASH
                        else (n, shell.RECUSADO))
    cfg = json.loads(next(iter(opencode.renderizar(_cm(tmp_path)).arquivos_externos.values())))
    assert cfg["shell"] == absoluto


def test_opencode_fora_do_windows_omite_shell(tmp_path, monkeypatch):
    # Fora do Windows o shell do sistema resolve; o Koine não decide por ele.
    _isolar_home(monkeypatch, tmp_path / "home")
    monkeypatch.setattr(sys, "platform", "darwin")
    cfg = json.loads(next(iter(opencode.renderizar(_cm(tmp_path)).arquivos_externos.values())))
    assert "shell" not in cfg


def test_opencode_bootstrap_windows_tambem_declara_shell(tmp_path, monkeypatch):
    # A primeira sessão numa pasta é bootstrap; é onde o usuário novo esbarra.
    _isolar_home(monkeypatch, tmp_path / "home")
    monkeypatch.setattr(sys, "platform", "win32")
    _forcar_sonda(monkeypatch, {shell.PWSH: shell.EXECUTOU})
    cm = _cm(tmp_path, bootstrap=True, escopo_path="", indice_paths=[])
    cfg = json.loads(next(iter(opencode.renderizar(cm).arquivos_externos.values())))
    assert cfg["shell"] == "pwsh"
    assert cfg["instructions"] == [cm.usuario_path, cm.koine_path, cm.agente_path,
                                   cm.contexto_path]


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
