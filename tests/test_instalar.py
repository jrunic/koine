# tests/test_instalar.py
import os

from koine import instalar, paths


def _semear(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    for k in ("XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME"):
        monkeypatch.delenv(k, raising=False)
    src = tmp_path / "src"
    (src / "habilidades" / "kn-99-encerra-sessao").mkdir(parents=True)
    (src / "dominios").mkdir()
    (src / "KOINE.md").write_text("v1")
    (src / "habilidades" / "kn-99-encerra-sessao" / "SKILL.md").write_text("skill v1")
    (src / "dominios" / "tecnologia.md").write_text("dom v1")
    return src


def test_shipped_divergente_atualiza_e_guarda_o_anterior(tmp_path, monkeypatch):
    src = _semear(tmp_path, monkeypatch)
    instalar.extrair(str(src), "0.0.1")
    (src / "KOINE.md").write_text("v2")

    trocas, preservados = instalar.extrair(str(src), "0.0.2")

    # 1. a coisa que o usuário queria: o arquivo ficou NOVO
    assert open(os.path.join(paths.vault_dir(), "KOINE.md")).read() == "v2"
    # 2. e o que estava lá é recuperável — asserção SEPARADA, de propósito:
    #    juntas, elas passariam num mundo em que a atualização não aconteceu
    assert len(trocas) == 1
    destino, bak = trocas[0]
    assert destino.endswith("KOINE.md")
    assert open(bak).read() == "v1"
    assert paths.cache_dir() in bak


def test_dominios_do_usuario_seguem_preservados(tmp_path, monkeypatch):
    src = _semear(tmp_path, monkeypatch)
    instalar.extrair(str(src), "0.0.1")
    dom = os.path.join(paths.config_dir(), "dominios", "tecnologia.md")
    open(dom, "w").write("edicao do usuario")
    (src / "dominios" / "tecnologia.md").write_text("dom v2")

    trocas, preservados = instalar.extrair(str(src), "0.0.2")

    assert open(dom).read() == "edicao do usuario"
    assert any("dominios" in p for p in preservados)


def test_reextrair_o_mesmo_conteudo_nao_troca_nada(tmp_path, monkeypatch):
    src = _semear(tmp_path, monkeypatch)
    instalar.extrair(str(src), "0.0.1")

    trocas, preservados = instalar.extrair(str(src), "0.0.1")

    assert trocas == []
