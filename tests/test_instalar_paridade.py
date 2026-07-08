import json
import os

from koine import instalar
from tests import _parity

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT = os.path.join(REPO, "vault")


def test_extracao_bate_com_go(tmp_path, monkeypatch):
    home_go = str(tmp_path / "go")
    home_py = str(tmp_path / "py")
    os.makedirs(home_go)
    os.makedirs(home_py)

    # Go: extrai no home_go (efeitos colaterais isolados)
    _parity.instalar_go(home_go)

    # Python: extrai no home_py
    monkeypatch.setenv("HOME", home_py)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    instalar.extrair(VAULT, "0.4.0-dev", force=False)

    # compara SÓ o que o P2 cobre: vault em DATA + dominios em CONFIG
    for sub in (".local/share/koine", ".config/koine/dominios"):
        go = _parity.arvore(os.path.join(home_go, sub))
        py = _parity.arvore(os.path.join(home_py, sub))
        go.pop(".meta.json", None)
        py.pop(".meta.json", None)  # timestamp difere
        assert py == go, f"divergência em {sub}"


def test_meta_json_gravado(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    instalar.extrair(VAULT, "9.9.9", force=False)
    meta = json.load(open(tmp_path / ".local/share/koine/.meta.json"))
    assert meta["versao"] == "9.9.9"
    assert meta["timestamp"].endswith("Z")


def test_idempotente_segunda_rodada_sem_divergencia(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    instalar.extrair(VAULT, "0.4.0-dev")
    div = instalar.extrair(VAULT, "0.4.0-dev")  # segunda vez
    assert div == []  # tudo idêntico → nenhuma divergência


def test_divergente_reportado_nao_sobrescrito(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    instalar.extrair(VAULT, "0.4.0-dev")
    koine_md = tmp_path / ".local/share/koine/KOINE.md"
    koine_md.write_text("ADULTERADO")
    div = instalar.extrair(VAULT, "0.4.0-dev")  # sem force
    assert str(koine_md) in div
    assert koine_md.read_text() == "ADULTERADO"  # não sobrescrito
    div2 = instalar.extrair(VAULT, "0.4.0-dev", force=True)
    assert koine_md.read_text() != "ADULTERADO"  # force sobrescreve
