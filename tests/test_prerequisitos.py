from koine import prerequisitos as pre
from koine import shell


def _sonda(mapa):
    def s(nome):
        return nome, mapa.get(nome, shell.AUSENTE)
    return s


NEGADO = {shell.PWSH: shell.RECUSADO, shell.POWERSHELL: shell.RECUSADO,
          shell.CMD: shell.EXECUTOU}
NEGADO_COM_BASH = dict(NEGADO, **{shell.BASH: shell.EXECUTOU})
SAUDAVEL = {shell.PWSH: shell.EXECUTOU, shell.POWERSHELL: shell.EXECUTOU,
            shell.CMD: shell.EXECUTOU}


def test_copilot_sem_shell_onde_a_politica_nega():
    a = pre.avaliar_cliente("copilot", sonda=_sonda(NEGADO_COM_BASH))
    assert a.codigo == pre.SEM_SHELL
    assert a.cliente == "copilot"


def test_o_git_bash_nao_salva_copilot_codex_nem_agy():
    # É a medição da #673: os três nunca tentam bash, tendo-o disponível.
    for cliente in ("copilot", "codex", "agy"):
        a = pre.avaliar_cliente(cliente, sonda=_sonda(NEGADO_COM_BASH))
        assert a.codigo == pre.SEM_SHELL, cliente


def test_claude_com_git_bash_esta_bem():
    assert pre.avaliar_cliente("claude", sonda=_sonda(NEGADO_COM_BASH)) is None


def test_claude_sem_git_bash_tem_remedio_proprio():
    # Achado distinto do SEM_SHELL: aqui existe o que fazer.
    a = pre.avaliar_cliente("claude", sonda=_sonda(NEGADO))
    assert a.codigo == pre.CLAUDE_SEM_BASH


def test_opencode_nunca_fica_sem_shell():
    # O cmd é o piso desde a #674.
    assert pre.avaliar_cliente("opencode", sonda=_sonda(NEGADO)) is None


def test_maquina_saudavel_nao_produz_achado():
    for cliente in ("claude", "opencode", "copilot", "codex", "agy"):
        assert pre.avaliar_cliente(cliente, sonda=_sonda(SAUDAVEL)) is None, cliente
