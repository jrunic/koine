"""Pass-through de flags do usuário para o cliente IA.

`kn-claude hermes . --chrome` → o `--chrome` vai pro claude. O usuário escolhe
quando ligar; a lib só separa posicionais (agente, pasta) das flags e repassa.
"""
from koine import cli


def test_separar_args():
    s = cli._separar_args
    assert s(["hermes"]) == (["hermes"], [])
    assert s(["hermes", "."]) == (["hermes", "."], [])
    assert s(["hermes", "--chrome"]) == (["hermes"], ["--chrome"])
    assert s(["hermes", ".", "--chrome"]) == (["hermes", "."], ["--chrome"])
    assert s(["--chrome", "hermes"]) == (["hermes"], ["--chrome"])          # ordem livre
    # `--` terminador: tudo depois é literal (flags com valor)
    assert s(["hermes", ".", "--", "--model", "sonnet"]) == (["hermes", "."], ["--model", "sonnet"])
    # flag antes de `--` combina com o que vem depois
    assert s(["hermes", "--chrome", "--", "--model", "x"]) == (["hermes"], ["--chrome", "--model", "x"])


def _seam(monkeypatch, cap):
    monkeypatch.setattr("koine.launch.lancar",
                        lambda cliente, pasta, **kw: cap.update(
                            cliente=cliente, pasta=pasta, args=kw.get("args")))


def test_flag_usuario_repassada_ao_cliente(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    cap = {}
    _seam(monkeypatch, cap)
    assert cli.main(["claude", "hermes", koine_home["trab"], "--chrome"]) == 0
    assert cap["args"] == ["--chrome"]
    assert cap["pasta"] == koine_home["trab"]  # `.` — pasta não confundida com a flag


def test_sem_flag_nao_repassa_nada(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    cap = {}
    _seam(monkeypatch, cap)
    cli.main(["claude", "hermes", koine_home["trab"]])
    assert cap["args"] is None  # sem flags → None (comportamento inalterado)


def test_flag_usuario_combina_com_extra_args_do_adapter(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    cap = {}
    _seam(monkeypatch, cap)
    cli.main(["codex", "hermes", koine_home["trab"], "--chrome"])
    # EXTRA_ARGS do codex (-c ...) PRIMEIRO, depois a flag do usuário
    assert cap["args"] == ["-c", "project_doc_max_bytes=1048576", "--chrome"]
