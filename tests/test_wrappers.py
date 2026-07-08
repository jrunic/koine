import os
import stat
from koine import wrappers


def _claude(criados):
    """Seleciona o wrapper kn-claude (o REGISTRY tem múltiplos adapters)."""
    (c,) = [p for p in criados if os.path.basename(p).split(".")[0] == "kn-claude"]
    return c


def test_gera_um_wrapper_por_adapter_registrado(tmp_path):
    bindir = str(tmp_path / "bin")
    pyz = "/opt/koine/koine.pyz"
    criados = wrappers.gerar(bindir, pyz)
    # wrapper admin `koine` + um kn-<cliente> por adapter registrado
    assert set(criados) == {
        os.path.join(bindir, "koine"),
        os.path.join(bindir, "kn-claude"),
        os.path.join(bindir, "kn-agy"),
        os.path.join(bindir, "kn-codex"),
        os.path.join(bindir, "kn-copilot"),
        os.path.join(bindir, "kn-opencode"),
    }


def test_wrapper_usa_interpretador_absoluto_quando_informado(tmp_path, monkeypatch):
    # BUG (encontrado empiricamente): `python3` puro no wrapper Unix pode
    # resolver para o Python 3.9 do sistema (macOS), que NÃO roda koine (3.12+).
    # Fix: o wrapper invoca o interpretador ABSOLUTO capturado na instalação
    # (sys.executable de quem rodou `instalar` — garantidamente >=3.10, senão
    # o próprio `instalar` teria falhado no import).
    monkeypatch.setattr(wrappers, "_is_windows", lambda: False)
    bindir = str(tmp_path / "bin")
    pyz = "/opt/koine/koine.pyz"
    interp = "/opt/py312/bin/python3.12"
    caminho = _claude(wrappers.gerar(bindir, pyz, interp))
    conteudo = open(caminho).read()
    assert f'exec "{interp}" "{pyz}" claude "$@"' in conteudo
    # e NÃO o python3 puro (a fonte do bug)
    assert "exec python3 " not in conteudo


def test_wrapper_unix_default_python3_e_executavel(tmp_path, monkeypatch):
    # Sem interpretador informado → fallback por plataforma (python3 no Unix).
    monkeypatch.setattr(wrappers, "_is_windows", lambda: False)
    bindir = str(tmp_path / "bin")
    pyz = "/opt/koine/koine.pyz"
    caminho = _claude(wrappers.gerar(bindir, pyz))
    conteudo = open(caminho).read()
    assert conteudo.startswith("#!/usr/bin/env bash")
    assert f'exec "python3" "{pyz}" claude "$@"' in conteudo
    assert os.stat(caminho).st_mode & stat.S_IXUSR  # bit de execução


def test_wrapper_windows_bat_usa_interpretador(tmp_path, monkeypatch):
    monkeypatch.setattr(wrappers, "_is_windows", lambda: True)
    bindir = str(tmp_path / "bin")
    interp = r"C:\Python313\python.exe"
    caminho = _claude(wrappers.gerar(bindir, r"C:\koine\koine.pyz", interp))
    assert caminho.endswith("kn-claude.bat")
    conteudo = open(caminho).read()
    assert '@"C:\\Python313\\python.exe" "C:\\koine\\koine.pyz" claude %*' in conteudo


def test_wrapper_windows_default_python(tmp_path, monkeypatch):
    # Sem interpretador → fallback `python` no Windows (o que a TI do Aldo instalou).
    monkeypatch.setattr(wrappers, "_is_windows", lambda: True)
    bindir = str(tmp_path / "bin")
    caminho = _claude(wrappers.gerar(bindir, r"C:\koine\koine.pyz"))
    assert '@"python" "C:\\koine\\koine.pyz" claude %*' in open(caminho).read()


def test_wrapper_admin_koine_sem_cliente(tmp_path, monkeypatch):
    monkeypatch.setattr(wrappers, "_is_windows", lambda: False)
    bindir = str(tmp_path / "bin")
    criados = wrappers.gerar(bindir, "/opt/koine/koine.pyz", "/opt/py/python3.12")
    (k,) = [p for p in criados if os.path.basename(p) == "koine"]
    # sem argumento de cliente — `koine versao`, `koine instalar` etc.
    assert 'exec "/opt/py/python3.12" "/opt/koine/koine.pyz" "$@"' in open(k).read()


def _layout_go(tmp_path):
    """Simula a instalação Go v0.3.x: binário kn-agente + symlinks kn-*."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    go_bin = bindir / "kn-agente"
    go_bin.write_bytes(b"\x7fELF-fake-binario-go")
    for n in ("kn-claude", "kn-agy", "kn-copilot", "kn-opencode", "kn-codex"):
        os.symlink(str(go_bin), str(bindir / n))
    return str(bindir), str(go_bin)


def test_upgrade_substitui_symlinks_da_instalacao_go(tmp_path, monkeypatch):
    monkeypatch.setattr(wrappers, "_is_windows", lambda: False)
    bindir, go_bin = _layout_go(tmp_path)
    criados = wrappers.gerar(bindir, "/opt/koine/koine.pyz", "/opt/py/python3.12")
    w = os.path.join(bindir, "kn-claude")
    assert w in criados
    assert not os.path.islink(w)  # symlink Go substituído por wrapper regular
    assert 'exec "/opt/py/python3.12" "/opt/koine/koine.pyz" claude "$@"' in open(w).read()
    # o binário Go NÃO foi corrompido (escrever através do symlink seria o bug)
    assert open(go_bin, "rb").read() == b"\x7fELF-fake-binario-go"
    # re-instalação: wrapper NOSSO (arquivo regular contendo koine.pyz) regenera
    criados2 = wrappers.gerar(bindir, "/opt/koine/koine.pyz", "/opt/py/python3.12")
    assert w in criados2


def test_conteudo_alheio_e_preservado_com_aviso(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(wrappers, "_is_windows", lambda: False)
    bindir = str(tmp_path / "bin")
    os.makedirs(bindir)
    # symlink para outro programa (não é instalação Koine)
    outro = tmp_path / "outro-programa"
    outro.write_text("#!/bin/sh\n")
    link = os.path.join(bindir, "kn-claude")
    os.symlink(str(outro), link)
    # script do PRÓPRIO usuário que por azar se chama kn-codex (sem koine.pyz)
    script = os.path.join(bindir, "kn-codex")
    with open(script, "w") as f:
        f.write("#!/bin/sh\necho meu-script\n")
    criados = wrappers.gerar(bindir, "/opt/koine/koine.pyz")
    assert os.path.islink(link) and os.readlink(link) == str(outro)   # intocado
    assert open(script).read() == "#!/bin/sh\necho meu-script\n"      # intocado
    assert link not in criados and script not in criados
    assert capsys.readouterr().out.count("preservado") == 2
