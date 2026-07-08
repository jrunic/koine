import io
import os
from koine import cli

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_instalar_extrai_e_cria_wrapper(tmp_path, monkeypatch):
    home = str(tmp_path)
    monkeypatch.setenv("HOME", home)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    # blindagem pytest -s: sem capture, sys.stdin é o TTY real → isatty=True
    monkeypatch.setattr("sys.stdin", io.StringIO())
    # vault_src explícito para o teste (não depende de localização automática)
    rc = cli.main(["instalar", "--vault", os.path.join(REPO, "vault"),
                   "--bin", str(tmp_path / "bin"), "--pyz", "/opt/koine/koine.pyz"])
    assert rc == 0
    # vault extraído
    assert os.path.exists(os.path.join(home, ".local/share/koine/KOINE.md"))
    assert os.path.exists(os.path.join(home, ".config/koine/dominios/tecnologia.md"))
    # wrapper criado (só kn-claude no P1)
    assert os.path.exists(os.path.join(str(tmp_path / "bin"), "kn-claude"))
