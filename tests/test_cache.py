from koine import cache


def test_slot_id_deterministico():
    a = cache.slot_id("/x/y")
    assert a == cache.slot_id("/x/y")
    assert len(a) == 12 and a != cache.slot_id("/x/z")


def test_caminho_bundle(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    b = cache.caminho_bundle("copilot-bundles", "abc")
    assert b.endswith("/.cache/koine/copilot-bundles/abc")


def test_caminho_arquivo(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    p = cache.caminho_arquivo("opencode-configs", "abc", "json")
    assert p.endswith("/.cache/koine/opencode-configs/abc.json")
