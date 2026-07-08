import os
from koine import cli
from tests import _parity

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_instalar_extrai_e_cria_wrapper(tmp_path, monkeypatch):
    home = str(tmp_path)
    monkeypatch.setenv("HOME", home)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    # vault_src explícito para o teste (não depende de localização automática)
    rc = cli.main(["instalar", "--vault", os.path.join(REPO, "vault"),
                   "--bin", str(tmp_path / "bin"), "--pyz", "/opt/koine/koine.pyz"])
    assert rc == 0
    # vault extraído
    assert os.path.exists(os.path.join(home, ".local/share/koine/KOINE.md"))
    assert os.path.exists(os.path.join(home, ".config/koine/dominios/tecnologia.md"))
    # wrapper criado (só kn-claude no P1)
    assert os.path.exists(os.path.join(str(tmp_path / "bin"), "kn-claude"))


def test_instalar_paridade_da_arvore(tmp_path, monkeypatch):
    home_go = str(tmp_path / "go"); os.makedirs(home_go)
    _parity.instalar_go(home_go)
    home_py = str(tmp_path / "py"); os.makedirs(home_py)
    monkeypatch.setenv("HOME", home_py)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    cli.main(["instalar", "--vault", os.path.join(REPO, "vault"),
              "--bin", str(tmp_path / "b"), "--pyz", "x"])
    for sub in (".local/share/koine", ".config/koine/dominios"):
        go = _parity.arvore(os.path.join(home_go, sub)); go.pop(".meta.json", None)
        py = _parity.arvore(os.path.join(home_py, sub)); py.pop(".meta.json", None)
        assert py == go
