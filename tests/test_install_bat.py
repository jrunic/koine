"""Guardas do scripts/release/install.bat.

O .bat roda em estação Windows corporativa onde o powershell.exe é bloqueado
por política — foi esse o defeito de produção (v0.6.1 e anteriores: o .bat era
um wrapper de `powershell -Command "iwr ... | iex"` e morria com "Acesso
negado"). Estas guardas prendem as duas propriedades que o defeito violava, e
que ninguém reexecuta à mão: nenhuma invocação de PowerShell, e arquivo em
ASCII puro (o cmd.exe lê .bat na codepage OEM; UTF-8 vira mojibake na tela,
como no print do incidente).
"""
import os
import re

BAT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "scripts", "release", "install.bat")


def _bytes() -> bytes:
    with open(BAT, "rb") as f:
        return f.read()


def test_install_bat_nao_invoca_powershell():
    texto = _bytes().decode("ascii", errors="replace").lower()
    # `powershell` pode ser CITADO em texto de orientação ao usuário; o que não
    # pode é ser INVOCADO. Casa o nome no início de um comando.
    invocacoes = [linha for linha in texto.splitlines()
                  if re.match(r"^\s*(@?)(call\s+|start\s+)?powershell(\.exe)?\b", linha)
                  or re.search(r"\bpwsh(\.exe)?\b", linha)]
    assert invocacoes == [], f"install.bat invoca PowerShell: {invocacoes}"


def test_install_bat_e_ascii_puro():
    dados = _bytes()
    nao_ascii = [(i, b) for i, b in enumerate(dados) if b > 0x7F]
    assert nao_ascii == [], (
        f"install.bat tem {len(nao_ascii)} byte(s) fora do ASCII "
        f"(primeiro no offset {nao_ascii[0][0] if nao_ascii else '-'}) — "
        "o cmd.exe renderiza isso como mojibake na codepage OEM")


def test_install_bat_tem_mensagem_e_saida_para_cada_falha():
    """Cada rótulo de falha imprime algo e sai com código != 0 — sem rótulo
    mudo, que é o que produz 'Acesso negado' sem explicação."""
    texto = _bytes().decode("ascii", errors="replace")
    blocos = re.split(r"^:(\w+)\s*$", texto, flags=re.MULTILINE)
    # blocos = [preambulo, nome1, corpo1, nome2, corpo2, ...]
    encontrados = []
    for nome, corpo in zip(blocos[1::2], blocos[2::2]):
        if not (nome.startswith("falha_") or nome.startswith("sem_")):
            continue
        encontrados.append(nome)
        assert re.search(r"^echo \S", corpo, flags=re.MULTILINE), \
            f"rótulo :{nome} não imprime mensagem"
        assert "exit /b 1" in corpo, f"rótulo :{nome} não sai com erro"
    assert set(encontrados) >= {
        "sem_curl", "sem_python", "sem_versao",
        "falha_download", "falha_extracao", "falha_instalar",
    }, f"faltam rótulos de falha: {encontrados}"


def test_install_bat_tem_quebra_de_linha_crlf():
    """O cmd.exe tem casos de borda com .bat em LF puro (rótulo/goto). O
    `.gitattributes` marca `*.bat -text` para nenhum `autocrlf` reescrever."""
    dados = _bytes()
    assert b"\r\n" in dados
    assert dados.replace(b"\r\n", b"").count(b"\n") == 0, \
        "install.bat tem linha em LF puro"
