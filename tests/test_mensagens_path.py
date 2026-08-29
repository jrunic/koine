from koine import mensagens, pathenv


def test_adicionado_diz_que_corrigiu_e_manda_reabrir():
    txt = mensagens.path_resultado(pathenv.ADICIONADO, r"C:\bin", na_sessao=False)
    assert "reabra" in txt.lower()
    assert r"C:\bin" in txt


def test_ja_estava_e_fora_da_sessao_NAO_diz_que_falta_no_path():
    # É o conserto do aviso que mentia: a pasta ESTÁ no PATH; o que falta é o
    # processo novo.
    txt = mensagens.path_resultado(pathenv.JA_ESTAVA, r"C:\bin", na_sessao=False)
    assert "reabra" in txt.lower()
    assert "não está no seu PATH" not in txt


def test_ja_estava_e_na_sessao_nao_diz_nada():
    assert mensagens.path_resultado(pathenv.JA_ESTAVA, r"C:\bin", na_sessao=True) == ""


def test_falhou_cai_na_orientacao_manual_sem_powershell():
    # Na estação que motivou o ciclo o PowerShell é o que está bloqueado.
    txt = mensagens.path_resultado(pathenv.FALHOU, r"C:\bin", na_sessao=False)
    assert "sysdm.cpl" in txt
    assert "PowerShell" not in txt


def test_o_remedio_do_cliente_fora_do_path_passa_a_ser_o_proprio_koine(monkeypatch):
    # Antes o produto oferecia um comando PowerShell "se liberado"; agora ele
    # sabe consertar. Só o ramo Windows — no Unix o remédio é o shell profile.
    monkeypatch.setattr(mensagens.platform, "system", lambda: "Windows")
    txt = mensagens.cliente_nao_encontrado("copilot")
    assert "koine instalar" in txt
    assert "SetEnvironmentVariable" not in txt
