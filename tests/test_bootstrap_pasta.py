"""Auto-guiar: launch numa pasta de sessão sem CONTEXTO.md válido.

Ver spec 20260724-spec-bootstrap-pasta-sessao. seam de launch = monkeypatch de
koine.launch.lancar (execvpe real mataria o pytest).
"""
import os

import pytest

from koine import bootstrap, cli, contexto


def _seam(monkeypatch):
    cap = {}
    monkeypatch.setattr("koine.launch.lancar",
                        lambda cliente, pasta, **kw: cap.update(cliente=cliente, pasta=pasta))
    return cap


# ---- classificar() ---------------------------------------------------------

def test_classificar_ausente(tmp_path):
    assert bootstrap.classificar(str(tmp_path)) == bootstrap.AUSENTE


def test_classificar_vazio(tmp_path):
    (tmp_path / "CONTEXTO.md").write_text("")
    assert bootstrap.classificar(str(tmp_path)) == bootstrap.VAZIO
    (tmp_path / "CONTEXTO.md").write_text("   \n\n")
    assert bootstrap.classificar(str(tmp_path)) == bootstrap.VAZIO


def test_classificar_malformado(tmp_path):
    # tem conteúdo, FM sem escopo nem bootstrap
    (tmp_path / "CONTEXTO.md").write_text("# Anotações soltas\n\ntexto qualquer\n")
    assert bootstrap.classificar(str(tmp_path)) == bootstrap.MALFORMADO


def test_classificar_bootstrap(tmp_path):
    (tmp_path / "CONTEXTO.md").write_text("---\nbootstrap: true\n---\n")
    assert bootstrap.classificar(str(tmp_path)) == bootstrap.BOOTSTRAP


def test_classificar_valido(tmp_path):
    (tmp_path / "CONTEXTO.md").write_text("---\nescopo: fixture\n---\n# ok\n")
    assert bootstrap.classificar(str(tmp_path)) == bootstrap.VALIDO


# ---- launch: onboarded + ausente/vazio → materializa e lança Hermes --------

def test_launch_onboarded_ausente_materializa_e_lanca_hermes(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    cap = _seam(monkeypatch)
    nova = os.path.join(koine_home["home"], "trabalho-novo")
    os.makedirs(nova)

    rc = cli.main(["claude", "jarvis", nova])  # agente inexistente de propósito

    assert rc == 0
    ctx = os.path.join(nova, "CONTEXTO.md")
    assert "bootstrap: true" in open(ctx, encoding="utf-8").read()
    assert "/kn-02-mantem-catalogo" in open(ctx, encoding="utf-8").read()
    # bootstrap ignora o agente pedido e força Hermes → CLAUDE.md referencia hermes.md
    claude = open(os.path.join(nova, "CLAUDE.md"), encoding="utf-8").read()
    assert "hermes.md" in claude
    assert cap == {"cliente": "claude", "pasta": nova}


def test_launch_onboarded_vazio_materializa(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    _seam(monkeypatch)
    nova = os.path.join(koine_home["home"], "trabalho-vazio")
    os.makedirs(nova)
    open(os.path.join(nova, "CONTEXTO.md"), "w").close()  # vazio

    assert cli.main(["claude", "hermes", nova]) == 0
    assert "bootstrap: true" in open(os.path.join(nova, "CONTEXTO.md"), encoding="utf-8").read()


# ---- launch: onboarded + malformado → erro amigável, preserva --------------

def test_launch_onboarded_malformado_erra_e_preserva(koine_home, monkeypatch, capsys):
    monkeypatch.setenv("HOME", koine_home["home"])
    _seam(monkeypatch)
    nova = os.path.join(koine_home["home"], "trabalho-malf")
    os.makedirs(nova)
    original = "# Meu trabalho\n\nconteúdo importante do usuário\n"
    open(os.path.join(nova, "CONTEXTO.md"), "w", encoding="utf-8").write(original)

    rc = cli.main(["claude", "hermes", nova])

    assert rc == 1
    assert open(os.path.join(nova, "CONTEXTO.md"), encoding="utf-8").read() == original  # preservado
    assert not os.path.exists(os.path.join(nova, "CLAUDE.md"))  # não materializou
    assert "incompleto" in capsys.readouterr().err


# ---- launch: NÃO onboarded → redirect, sem materializar --------------------

def test_launch_nao_onboarded_ausente_redireciona(tmp_path, monkeypatch, capsys):
    # HOME limpo: sem ~/.config/koine → não-onboarded
    home = str(tmp_path / "home"); os.makedirs(home)
    monkeypatch.setenv("HOME", home)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    _seam(monkeypatch)
    nova = os.path.join(home, "qualquer"); os.makedirs(nova)

    rc = cli.main(["claude", "jarvis", nova])

    assert rc == 1
    assert not os.path.exists(os.path.join(nova, "CONTEXTO.md"))  # nada materializado
    err = capsys.readouterr().err
    assert "koine instalar" in err
    assert "kn-claude hermes koine" in err


# ---- launch: symlink no lugar do CONTEXTO → conflito -----------------------

def test_launch_onboarded_symlink_erra(koine_home, monkeypatch, capsys):
    monkeypatch.setenv("HOME", koine_home["home"])
    _seam(monkeypatch)
    nova = os.path.join(koine_home["home"], "trabalho-sym"); os.makedirs(nova)
    alvo = os.path.join(nova, "alvo.md"); open(alvo, "w").close()
    os.symlink(alvo, os.path.join(nova, "CONTEXTO.md"))  # symlink p/ arquivo vazio → VAZIO

    rc = cli.main(["claude", "hermes", nova])

    assert rc == 1
    assert "symlink" in capsys.readouterr().err


# ---- regressões: bootstrap existente e válido inalterados ------------------

def test_launch_bootstrap_existente_inalterado(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    cap = _seam(monkeypatch)
    nova = os.path.join(koine_home["home"], "trab-boot"); os.makedirs(nova)
    conteudo = "---\nbootstrap: true\n---\n# meu bootstrap\n"
    open(os.path.join(nova, "CONTEXTO.md"), "w", encoding="utf-8").write(conteudo)

    assert cli.main(["claude", "hermes", nova]) == 0
    # não sobrescreveu o CONTEXTO bootstrap do usuário
    assert open(os.path.join(nova, "CONTEXTO.md"), encoding="utf-8").read() == conteudo
    assert cap["pasta"] == nova


def test_launch_valido_inalterado(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    cap = _seam(monkeypatch)
    # a fixture já tem pasta de trabalho com CONTEXTO válido (escopo: fixture)
    assert cli.main(["claude", "hermes", koine_home["trab"]]) == 0
    assert cap == {"cliente": "claude", "pasta": koine_home["trab"]}


# ---- gerar / mostrar: erro amigável sem materializar -----------------------

def test_gerar_ausente_erra_sem_escrever(koine_home, monkeypatch, capsys):
    monkeypatch.setenv("HOME", koine_home["home"])
    nova = os.path.join(koine_home["home"], "trab-gerar"); os.makedirs(nova)

    rc = cli.main(["gerar", "hermes", nova])

    assert rc == 1
    assert not os.path.exists(os.path.join(nova, "CLAUDE.md"))
    assert "CONTEXTO.md" in capsys.readouterr().err


def test_mostrar_ausente_erra(koine_home, monkeypatch, capsys):
    monkeypatch.setenv("HOME", koine_home["home"])
    nova = os.path.join(koine_home["home"], "trab-mostrar"); os.makedirs(nova)

    rc = cli.main(["mostrar", "hermes", nova])

    assert rc == 1
    assert "CONTEXTO.md" in capsys.readouterr().err


# ---- codex (cliente do Patrick/Aldo, adapter INLINE) pelo auto-guiar -------

def test_launch_codex_onboarded_ausente_materializa(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    cap = _seam(monkeypatch)
    nova = os.path.join(koine_home["home"], "trab-codex"); os.makedirs(nova)

    assert cli.main(["codex", "jarvis", nova]) == 0
    assert "bootstrap: true" in open(os.path.join(nova, "CONTEXTO.md"), encoding="utf-8").read()
    # codex é INLINE (não @path): a instrução kn-02 só desbloqueia o usuário se o
    # corpo do CONTEXTO for EMBUTIDO no AGENTS.md (snapshot). Provar conteúdo, não
    # só existência — "arquivo existe" ≠ "Hermes sabe rodar a entrevista".
    agents = open(os.path.join(nova, "AGENTS.md"), encoding="utf-8").read()
    assert "/kn-02-mantem-catalogo" in agents
    assert "hermes" in agents.lower()
    assert cap["cliente"] == "codex"
