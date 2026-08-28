from koine import shell


def _sonda_falsa(mapa):
    """mapa: nome do degrau → estado. Invocação é o próprio nome."""
    def sonda(nome):
        return nome, mapa.get(nome, shell.AUSENTE)
    return sonda


def test_melhor_escolhe_o_primeiro_degrau_que_executa():
    sonda = _sonda_falsa({shell.PWSH: shell.EXECUTOU, shell.BASH: shell.EXECUTOU})
    d = shell.melhor(shell.ESCADA, sonda=sonda)
    assert d.nome == shell.PWSH
    assert d.invocacao == "pwsh"


def test_melhor_pula_degrau_recusado():
    # é a estação corporativa: o pwsh existe, está no PATH e a política nega.
    sonda = _sonda_falsa({shell.PWSH: shell.RECUSADO,
                          shell.POWERSHELL: shell.RECUSADO,
                          shell.BASH: shell.EXECUTOU})
    assert shell.melhor(shell.ESCADA, sonda=sonda).nome == shell.BASH


def test_melhor_respeita_os_degraus_que_o_cliente_aceita():
    # o claude não aceita cmd; com tudo recusado menos cmd, não há degrau.
    sonda = _sonda_falsa({shell.CMD: shell.EXECUTOU})
    assert shell.melhor((shell.PWSH, shell.POWERSHELL, shell.BASH), sonda=sonda) is None
    assert shell.melhor(shell.ESCADA, sonda=sonda).nome == shell.CMD
