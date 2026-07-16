from koine import cli, launch, mensagens


def test_cliente_nao_encontrado_windows_guia_path(monkeypatch):
    monkeypatch.setattr(mensagens.platform, "system", lambda: "Windows")
    msg = mensagens.cliente_nao_encontrado("codex")
    assert "não encontrado no PATH" in msg
    assert "where codex" in msg  # diagnóstico Windows
    assert "SetEnvironmentVariable" in msg  # correção de PATH sem admin


def test_cliente_nao_encontrado_unix_guia_path(monkeypatch):
    monkeypatch.setattr(mensagens.platform, "system", lambda: "Darwin")
    msg = mensagens.cliente_nao_encontrado("claude")
    assert "command -v claude" in msg
    assert "export PATH" in msg


def test_cliente_nao_executavel_diz_que_nao_e_path():
    msg = mensagens.cliente_nao_executavel("codex", r"C:\x\codex.exe")
    assert r"C:\x\codex.exe" in msg  # aponta o caminho resolvido
    assert "NÃO é um erro de PATH" in msg
    assert "WinError 193" in msg


def test_rodar_cliente_ausente_imprime_amigavel(koine_home, monkeypatch, capsys):
    """Integração: cliente fora do PATH → mensagem amigável no stderr, rc=1."""
    monkeypatch.setenv("HOME", koine_home["home"])

    def nao_encontrado(cliente, pasta, **kw):
        raise launch.ClienteNaoEncontrado(cliente)

    monkeypatch.setattr("koine.launch.lancar", nao_encontrado)
    rc = cli.main(["claude", "hermes", koine_home["trab"]])
    assert rc == 1
    err = capsys.readouterr().err
    assert "não encontrado no PATH" in err
    assert "claude" in err
