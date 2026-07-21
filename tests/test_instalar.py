# tests/test_instalar.py
import os
from koine import instalar, paths


def test_atualizar_vault_forca_vault_preserva_dominios(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    for k in ("XDG_DATA_HOME", "XDG_CONFIG_HOME"):
        monkeypatch.delenv(k, raising=False)
    src = tmp_path / "src"
    (src / "conceitos").mkdir(parents=True)
    (src / "dominios").mkdir()
    (src / "KOINE.md").write_text("v1")
    (src / "dominios" / "tecnologia.md").write_text("dom v1")
    instalar.extrair(str(src), "0.0.1")
    dom = os.path.join(paths.config_dir(), "dominios", "tecnologia.md")
    open(dom, "w").write("edicao do usuario")
    (src / "KOINE.md").write_text("v2")
    div = instalar.extrair(str(src), "0.0.2", force=False, atualizar_vault=True)
    assert open(os.path.join(paths.vault_dir(), "KOINE.md")).read() == "v2"
    assert open(dom).read() == "edicao do usuario"
    assert any("dominios" in d for d in div)
