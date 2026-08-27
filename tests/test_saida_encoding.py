"""Saída do Koine num stdout que não é console — o caso Windows.

No Windows, quando o stdout é console, o Python escreve por WriteConsoleW e
qualquer caractere passa. Redirecionado (arquivo, pipe, tarefa agendada), o
encoding vira o do locale — `cp1252` — e o `✓` das mensagens derruba o comando
com UnicodeEncodeError. Medido em produção na bancada Windows em 27/08/2026:
`install.bat` rodando por tarefa agendada abortou o `koine instalar` no
primeiro `print` com símbolo.

`PYTHONIOENCODING=cp1252` reproduz o mesmo stdout em qualquer sistema.
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pyz(tmp_path):
    out = str(tmp_path / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"), "--out", out],
                   check=True, capture_output=True, text=True)
    return os.path.join(out, "koine.pyz")


def test_instalar_com_stdout_cp1252_nao_quebra(tmp_path):
    pyz = _pyz(tmp_path)
    home = str(tmp_path / "home"); os.makedirs(home)
    r = subprocess.run(
        [sys.executable, pyz, "instalar"],
        env={"HOME": home, "USERPROFILE": home, "PATH": "/usr/bin:/bin",
             "PYTHONIOENCODING": "cp1252"},
        capture_output=True, timeout=90, stdin=subprocess.DEVNULL)
    # bytes, não text=True: a saída é cp1252 de propósito, e decodificá-la como
    # utf-8 faria o TESTE quebrar em vez de medir o processo.
    saida = r.stdout.decode("cp1252", "replace")
    erro = r.stderr.decode("cp1252", "replace")
    assert "UnicodeEncodeError" not in erro, (
        "o instalar quebrou ao escrever em stdout não-UTF-8:\n" + erro[-1500:])
    assert r.returncode == 0, erro[-1500:]
    # e o que ele quis dizer chegou, ainda que o símbolo tenha virado outro char
    assert "Pasta can" in saida and "nica em" in saida


def test_preparar_deixa_utf8_intacto():
    """Não mexer em quem já está bem: em UTF-8 o `errors` continua `strict`,
    então erro de encoding num fluxo capaz vira falha visível, não `?` mudo."""
    import io
    from koine import saida
    f = io.TextIOWrapper(io.BytesIO(), encoding="utf-8", errors="strict")
    saida.preparar(f)
    assert f.errors == "strict"


def test_preparar_troca_a_politica_de_erro_fora_do_utf8():
    import io
    from koine import saida
    f = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    saida.preparar(f)
    assert f.errors == "replace"
    f.write("✓ ok, cabeçalho")   # nao levanta
    f.flush()


def test_preparar_ignora_fluxo_sem_reconfigure():
    """Fluxo substituído em teste (StringIO, capsys) não tem reconfigure — a
    saída é o meio, nunca o motivo de uma falha."""
    import io
    from koine import saida
    saida.preparar(io.StringIO())   # nao levanta
