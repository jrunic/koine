import os

import pytest
from tests.fixtures import seed


@pytest.fixture(autouse=True)
def _isola_xdg(monkeypatch):
    # Runners CI (GitHub Actions ubuntu) exportam XDG_CONFIG_HOME etc.
    # paths.py honra XDG_* ANTES de HOME; sem esta limpeza, XDG_* herdado
    # vaza para o processo do teste e para todo subprocesso montado com
    # {**os.environ, "HOME": <fixture>} (pyz, wrappers, installers),
    # resolvendo config no HOME real do runner em vez do HOME isolado.
    # Testes que precisam de XDG_* setam explicitamente via monkeypatch
    # (roda após esta fixture).
    for k in list(os.environ):
        if k.startswith("XDG_"):
            monkeypatch.delenv(k, raising=False)
    # Mesmo motivo do XDG_*: o diagnóstico do Paseo resolve o home por esta
    # variável, e herdá-la faria a suíte medir a máquina de quem roda.
    monkeypatch.delenv("PASEO_HOME", raising=False)


@pytest.fixture
def koine_home(tmp_path):
    return seed.montar(str(tmp_path))


class _ResultadoInerte:
    """Resposta padrão para qualquer subprocesso real do Paseo que um teste
    não pediu — nunca 0, nunca "true", sempre lido como "não deu para
    fazer" pelos dois consumidores (`_rodar`/`_rodar_paseo`) e pelas
    checagens de `paseo_app`."""
    returncode = 1
    stdout = ""
    stderr = ""


def _alvo_paseo_real(cmd) -> bool:
    """True só quando `cmd` é literalmente o binário `paseo` ou um comando
    de controle do app `Paseo` (osascript/open) — nunca por substring, para
    não capturar path de teste que por acaso contenha "paseo" no meio."""
    partes = [cmd] if isinstance(cmd, (str, bytes)) else [str(c) for c in cmd]
    if not partes:
        return False
    if any(os.path.basename(p).lower() in
          ("paseo", "paseo.cmd", "paseo.exe", "paseo.bat") for p in partes):
        return True
    if partes[0] in ("osascript", "open"):
        return any("Paseo" in p for p in partes)
    return False


@pytest.fixture(autouse=True)
def _bloqueia_paseo_real(monkeypatch):
    # Incidente de 22/09/2026: um teste sem isolamento explícito da camada
    # Paseo (ex.: cli.main(["instalar", ...]) sem mockar skills.detectar_
    # harnesses/paseo_app) alcançou, sem querer, o `paseo` e o app Paseo
    # REAIS desta máquina — derrubou a sessão do Paseo em uso e criou
    # projeto/workspace lixo apontando para pasta temporária de teste.
    #
    # PRIMEIRA versão deste fixture patcheava `subprocess.run` incondicio-
    # nalmente — e quebrou 16 testes sem nenhuma relação com Paseo (build do
    # pyz, shim, fzf, wrappers): `paseo_ambiente.subprocess` e `paseo_app.
    # subprocess` são o MESMO objeto de módulo que `subprocess` em qualquer
    # outro arquivo do processo — substituir `.run` nele afeta TODO mundo,
    # não só quem importou via `paseo_ambiente`/`paseo_app`. A correção é
    # filtrar pelo COMANDO, não pelo ponto de import: passa direto para o
    # `subprocess.run` real qualquer coisa que não seja literalmente o
    # binário `paseo` ou um `osascript`/`open` mirando o app `Paseo`.
    #
    # `resolver_executavel` faz só descoberta de PATH (sem efeito) e por
    # isso não é tocado aqui — os testes de `test_paseo_ambiente.py` que o
    # chamam direto continuam vendo o comportamento real. Teste que PRECISA
    # exercitar o caminho real sobrescreve `subprocess.run` dentro do
    # próprio teste — como `test_paseo_ambiente.py`, `test_paseo_app.py` e
    # `test_instalar_paseo_onboarding.py` já fazem; o `setattr` deles ocorre
    # DEPOIS deste fixture (autouse roda primeiro) e vale para aquele teste.
    import subprocess as _subprocess_mod
    real_run = _subprocess_mod.run

    def _run_filtrado(cmd, *args, **kwargs):
        if _alvo_paseo_real(cmd):
            return _ResultadoInerte()
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(_subprocess_mod, "run", _run_filtrado)


@pytest.fixture(scope="session", autouse=True)
def _marcador_bloqueio_paseo_sessao():
    # Segunda camada do mesmo incidente (22-24/09/2026): `_bloqueia_paseo_
    # real` acima só protege chamadas de subprocess DENTRO deste processo
    # pytest. Vários testes e2e sobem o `koine.pyz` como PROCESSO FILHO real
    # (`subprocess.run([sys.executable, pyz, "instalar", ...])`) — um
    # interpretador novo, sem nenhum monkeypatch alcançando ele — e
    # `paseo_ambiente.resolver_executavel` tem fallback fixo fora do PATH
    # (`/Applications/Paseo.app/...`), então mesmo com PATH isolado no
    # filho, o Paseo real É encontrado. `paseo_app.py` checa este arquivo
    # (`MARCADOR_BLOQUEIO`) antes de qualquer `osascript`/`open` real — é o
    # único sinal que qualquer processo filho, em qualquer máquina, enxerga
    # igual, porque vários desses testes constroem `env={}` do zero para o
    # filho, sem herdar nada deste processo (variável de ambiente não
    # chegaria lá). Criado uma vez para a suíte inteira; removido ao fim,
    # inclusive se a suíte for interrompida no meio (try/finally).
    from koine.paseo_app import MARCADOR_BLOQUEIO
    with open(MARCADOR_BLOQUEIO, "w") as f:
        f.write("suite de testes do koine em andamento — nao remova\n")
    try:
        yield
    finally:
        try:
            os.remove(MARCADOR_BLOQUEIO)
        except FileNotFoundError:
            pass


@pytest.fixture(autouse=True)
def _limpa_cache_de_shell():
    # A sonda e memoizada por processo, e o pytest e UM processo para a suite
    # inteira. Sem zerar entre testes, o cenario de um contamina o seguinte.
    from koine import shell
    shell.limpar_cache()
    yield
    shell.limpar_cache()
