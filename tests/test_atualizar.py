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
