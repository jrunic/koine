# tests/test_atualizar.py
import hashlib
import pytest
from koine import atualizar


def test_versao_pinada_por_env(monkeypatch):
    monkeypatch.setenv("KOINE_VERSAO", "v0.9.9")
    assert atualizar.resolver_versao() == ("v0.9.9", "0.9.9")


def test_versao_pinada_sem_v(monkeypatch):
    monkeypatch.setenv("KOINE_VERSAO", "0.9.9")
    assert atualizar.resolver_versao() == ("v0.9.9", "0.9.9")


def test_versao_latest_github(monkeypatch):
    monkeypatch.delenv("KOINE_VERSAO", raising=False)

    class FakeResp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def geturl(self): return "https://github.com/jrunic/koine/releases/tag/v1.2.3"

    capturado = {}

    def fake_urlopen(req, timeout=30):
        capturado["ua"] = req.get_header("User-agent")
        return FakeResp()

    monkeypatch.setattr(atualizar.urllib.request, "urlopen", fake_urlopen)
    assert atualizar.resolver_versao() == ("v1.2.3", "1.2.3")
    assert capturado["ua"]  # github exige User-Agent


def test_monta_urls_default(monkeypatch):
    monkeypatch.delenv("KOINE_BASE_URL", raising=False)
    zip_url, sha_url = atualizar.montar_urls("v0.4.3", "0.4.3")
    assert zip_url == "https://github.com/jrunic/koine/releases/download/v0.4.3/koine-0.4.3.zip"
    assert sha_url == "https://github.com/jrunic/koine/releases/download/v0.4.3/SHA256SUMS"


def test_monta_urls_espelho(monkeypatch):
    monkeypatch.setenv("KOINE_BASE_URL", "http://espelho.interno/koine")
    zip_url, _ = atualizar.montar_urls("v0.4.3", "0.4.3")
    assert zip_url == "http://espelho.interno/koine/v0.4.3/koine-0.4.3.zip"


def test_verifica_sha256_ok():
    dados = b"conteudo do zip"
    h = hashlib.sha256(dados).hexdigest()
    atualizar.verificar_sha256(dados, f"{h}  koine-0.4.3.zip\n", "koine-0.4.3.zip")


def test_verifica_sha256_divergente():
    with pytest.raises(atualizar.AtualizarErro):
        atualizar.verificar_sha256(b"x", "deadbeef  koine-0.4.3.zip\n", "koine-0.4.3.zip")


import os


def test_substituir_pyz_sucesso(tmp_path):
    src = tmp_path / "novo.pyz"; src.write_bytes(b"novo")
    dst = tmp_path / "dist" / "koine.pyz"; dst.parent.mkdir(); dst.write_bytes(b"velho")
    atualizar._substituir_pyz(str(src), str(dst))
    assert dst.read_bytes() == b"novo" and not src.exists()


def test_substituir_pyz_retenta_em_permissionerror(tmp_path, monkeypatch):
    src = tmp_path / "novo.pyz"; src.write_bytes(b"novo")
    dst = tmp_path / "koine.pyz"; dst.write_bytes(b"velho")
    n = {"c": 0}
    real = os.replace

    def flaky(a, b):
        n["c"] += 1
        if n["c"] < 3:
            raise PermissionError("em uso")
        real(a, b)

    monkeypatch.setattr(atualizar.os, "replace", flaky)
    monkeypatch.setattr(atualizar.time, "sleep", lambda _: None)
    atualizar._substituir_pyz(str(src), str(dst))
    assert dst.read_bytes() == b"novo" and n["c"] == 3


def test_refresh_skills_instala_nos_detectados(monkeypatch):
    chamados = []
    monkeypatch.setattr(atualizar.skills, "detectar_harnesses", lambda: ["claude", "codex"])
    monkeypatch.setattr(atualizar.skills, "instalar_habilidades_detalhado",
                        lambda h, force=False: (chamados.append((h, force)), (["kn-99"], [], []))[1])
    atualizar._refresh_skills(force=True)
    assert chamados == [("claude", True), ("codex", True)]


from koine._version import __version__


def test_preparar_noop_quando_ja_na_versao(monkeypatch, capsys):
    monkeypatch.setenv("KOINE_VERSAO", f"v{__version__}")
    baixou = {"n": 0}
    monkeypatch.setattr(atualizar, "baixar", lambda url: baixou.__setitem__("n", baixou["n"] + 1))
    assert atualizar.preparar(force=False) == (None, __version__)
    assert baixou["n"] == 0
    assert __version__ in capsys.readouterr().out


def test_mensagem_ja_recente():
    from koine import mensagens
    assert "0.4.3" in mensagens.atualizar_ja_recente("0.4.3")
