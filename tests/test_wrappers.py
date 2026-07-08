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
    # um wrapper kn-<cliente> por adapter registrado (claude + agy)
    assert set(criados) == {
        os.path.join(bindir, "kn-claude"),
        os.path.join(bindir, "kn-agy"),
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
