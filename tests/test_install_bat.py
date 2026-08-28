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


def test_install_bat_nao_expande_substring_de_variavel_talvez_vazia():
    """`%VAR:~i,n%` com VAR indefinida é erro de sintaxe FATAL no cmd, e um
    `if defined VAR` na MESMA linha não protege: o cmd expande a linha inteira
    antes de avaliar a condição. Foi assim que o caminho sem `KOINE_VERSAO`
    morreu com "A sintaxe do comando está incorreta" na bancada Windows
    (26/08/2026). A guarda: expansão de substring nunca compartilha linha com o
    `if defined` que deveria protegê-la."""
    texto = _bytes().decode("ascii", errors="replace")
    ofensoras = [linha for linha in texto.splitlines()
                 if re.search(r"%\w+:~", linha) and re.search(r"if\s+defined\s", linha, re.I)]
    assert ofensoras == [], (
        "expansão de substring guardada por `if defined` na mesma linha "
        f"(o cmd expande antes de avaliar): {ofensoras}")


def test_instaladores_repassam_args_do_instalar():
    """Sem isto, as flags do `koine instalar` são inalcançáveis para quem instala
    pelo one-liner — que é justamente o caminho da automação, onde o prompt
    trava. Uma flag que só existe para quem já tem o pyz na mão não resolve o
    problema que ela foi criada para resolver."""
    bat = _bytes().decode("ascii", errors="replace")
    sh_path = os.path.join(os.path.dirname(BAT), "install.sh")
    with open(sh_path, encoding="utf-8") as f:
        sh = f.read()
    assert "%KOINE_INSTALAR_ARGS%" in bat
    assert "KOINE_INSTALAR_ARGS:-" in sh, "sem o :- o `set -u` aborta o instalador"
    # o override tem que estar documentado no cabeçalho, junto dos outros
    assert "KOINE_INSTALAR_ARGS" in bat.split("REM ---")[0]
