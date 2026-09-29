import os

from koine import cli, paseo_app, paseo_configurar, paseo_provider, \
    paseo_workspace, paseo_diagnostico as pd, prerequisitos, skills


def _vault():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "vault")


def _instalar(koine_home, *args):
    bindir = os.path.join(koine_home["home"], "bin")
    return cli.main(["instalar", "--vault", _vault(), "--bin", bindir,
                     "--pyz", os.path.join(koine_home["home"], "koine.pyz"),
                     "--nao-interativo", "--para", "nenhum",
                     "--pasta-canonica", os.path.join(koine_home["home"], "koine"),
                     *args])


def _costura_feliz(monkeypatch, tmp_path, *, config_mudou=True,
                   ja_rodando=False):
    # Achado do CI (ubuntu-latest, 24/09/2026): _onboarding_paseo_se_aplicavel
    # sai cedo em `sys.platform != "darwin"` — sem forçar aqui, os testes só
    # exercitam o caminho real numa máquina macOS de verdade, e passam por
    # engano em qualquer outra plataforma (retorno antecipado = chamadas
    # nunca disparam, e os asserts de "não chamou" passam por motivo errado).
    monkeypatch.setattr(cli.sys, "platform", "darwin")
    monkeypatch.setattr(skills, "detectar_harnesses", lambda: ["claude"])
    monkeypatch.setattr(
        pd, "verificar_executaveis",
        lambda: pd.Verificacao("executaveis.paseo", pd.OK, "ok",
                               {"estado": "no-path"}))

    alteracoes = [object()] if config_mudou else []
    monkeypatch.setattr(
        paseo_configurar, "aplicar",
        lambda dry_run=False: paseo_configurar.Resultado(
            alteracoes=alteracoes, gravou=config_mudou, caminho=str(tmp_path)))
    monkeypatch.setattr(
        paseo_provider, "aplicar",
        lambda dry_run=False: paseo_provider.ResultadoProv(
            entries=[], gravou=config_mudou, caminho=str(tmp_path)))

    chamadas = {"esta_rodando": ja_rodando, "encerrou": False, "abriu": False}

    def fake_esta_rodando():
        return chamadas["esta_rodando"]

    def fake_encerrar():
        chamadas["encerrou"] = True
        chamadas["esta_rodando"] = False
        return True

    def fake_abrir():
        chamadas["abriu"] = True
        return True
    monkeypatch.setattr(paseo_app, "esta_rodando", fake_esta_rodando)
    monkeypatch.setattr(paseo_app, "encerrar", fake_encerrar)
    monkeypatch.setattr(paseo_app, "abrir", fake_abrir)
    monkeypatch.setattr(paseo_app, "aguardar_daemon", lambda **k: True)

    garantiu = {}
    monkeypatch.setattr(
        paseo_workspace, "garantir",
        lambda pasta, titulo="": garantiu.update(pasta=pasta, titulo=titulo) or
        {"projectId": "p", "workspaceId": "w", "acao": "criado"})

    monkeypatch.setattr(pd, "diagnosticar", lambda home=None: [])
    return chamadas, garantiu


def test_instalar_com_harness_paseo_compativel_conduz_a_sequencia(
        monkeypatch, tmp_path, koine_home):
    monkeypatch.setenv("HOME", koine_home["home"])
    chamadas, garantiu = _costura_feliz(monkeypatch, tmp_path)

    rc = _instalar(koine_home)

    assert rc == 0
    assert chamadas["abriu"] is True
    assert garantiu["pasta"] == os.path.join(koine_home["home"], "koine")
    assert garantiu["titulo"] == "Koine"


def test_instalar_sem_harness_paseo_compativel_nao_toca_em_paseo(
        monkeypatch, tmp_path, koine_home):
    monkeypatch.setenv("HOME", koine_home["home"])
    monkeypatch.setattr(skills, "detectar_harnesses", lambda: ["codex"])
    tocou = []
    monkeypatch.setattr(paseo_app, "abrir", lambda: tocou.append("abriu") or True)

    rc = _instalar(koine_home)

    assert rc == 0
    assert tocou == []


def test_instalar_com_paseo_ja_aberto_e_config_inalterada_nao_reinicia(
        monkeypatch, tmp_path, koine_home):
    monkeypatch.setenv("HOME", koine_home["home"])
    chamadas, _ = _costura_feliz(monkeypatch, tmp_path, config_mudou=False,
                                 ja_rodando=True)

    rc = _instalar(koine_home)

    assert rc == 0
    assert chamadas["encerrou"] is False


def test_instalar_com_paseo_ja_aberto_e_config_mudou_reinicia(
        monkeypatch, tmp_path, koine_home):
    monkeypatch.setenv("HOME", koine_home["home"])
    chamadas, _ = _costura_feliz(monkeypatch, tmp_path, config_mudou=True,
                                 ja_rodando=True)

    rc = _instalar(koine_home)

    assert rc == 0
    assert chamadas["encerrou"] is True
    assert chamadas["abriu"] is True


def test_modulo_app_desktop_escolhe_por_plataforma(monkeypatch):
    from koine import paseo_app_windows
    monkeypatch.setattr(cli.sys, "platform", "darwin")
    assert cli._modulo_app_desktop() is paseo_app
    monkeypatch.setattr(cli.sys, "platform", "win32")
    assert cli._modulo_app_desktop() is paseo_app_windows
    monkeypatch.setattr(cli.sys, "platform", "linux")
    assert cli._modulo_app_desktop() is None


def _costura_feliz_windows(monkeypatch, tmp_path, *, config_mudou=True,
                           ja_rodando=False, desktop_managed=True):
    """Espelho de `_costura_feliz`, mas forçando win32 e costurando
    `paseo_app_windows` em vez de `paseo_app`."""
    from koine import paseo_app_windows
    monkeypatch.setattr(cli.sys, "platform", "win32")
    monkeypatch.setattr(prerequisitos.shutil, "which", lambda n: None)
    monkeypatch.setattr(skills, "detectar_harnesses", lambda: ["claude"])
    monkeypatch.setattr(
        pd, "verificar_executaveis",
        lambda: pd.Verificacao("executaveis.paseo", pd.OK, "ok",
                               {"estado": "no-path"}))
    monkeypatch.setattr(pd, "desktop_managed", lambda: desktop_managed)

    alteracoes = [object()] if config_mudou else []
    monkeypatch.setattr(
        paseo_configurar, "aplicar",
        lambda dry_run=False: paseo_configurar.Resultado(
            alteracoes=alteracoes, gravou=config_mudou, caminho=str(tmp_path)))
    monkeypatch.setattr(
        paseo_provider, "aplicar",
        lambda dry_run=False: paseo_provider.ResultadoProv(
            entries=[], gravou=config_mudou, caminho=str(tmp_path)))

    chamadas = {"esta_rodando": ja_rodando, "encerrou": False, "abriu": False}

    def fake_esta_rodando():
        return chamadas["esta_rodando"]

    def fake_encerrar():
        # Só é chamado quando o orquestrador JÁ decidiu que desktop_managed
        # é True (pré-checado antes) — aqui sempre sucede.
        chamadas["encerrou"] = True
        chamadas["esta_rodando"] = False
        return True

    def fake_abrir():
        chamadas["abriu"] = True
        return True
    monkeypatch.setattr(paseo_app_windows, "esta_rodando", fake_esta_rodando)
    monkeypatch.setattr(paseo_app_windows, "encerrar", fake_encerrar)
    monkeypatch.setattr(paseo_app_windows, "abrir", fake_abrir)
    monkeypatch.setattr(paseo_app, "aguardar_daemon", lambda **k: True)

    garantiu = {}
    monkeypatch.setattr(
        paseo_workspace, "garantir",
        lambda pasta, titulo="": garantiu.update(pasta=pasta, titulo=titulo) or
        {"projectId": "p", "workspaceId": "w", "acao": "criado"})

    monkeypatch.setattr(pd, "diagnosticar", lambda home=None: [])
    return chamadas, garantiu


def test_instalar_no_windows_com_harness_conduz_a_sequencia(
        monkeypatch, tmp_path, koine_home):
    """Achado da spec 20260925: o Windows deixa de ser sempre-recusado —
    com harness Paseo-compatível e o mecanismo do módulo Windows, a
    sequência roda igual ao macOS."""
    monkeypatch.setenv("HOME", koine_home["home"])
    chamadas, garantiu = _costura_feliz_windows(monkeypatch, tmp_path)

    rc = _instalar(koine_home)

    assert rc == 0
    assert chamadas["abriu"] is True
    assert garantiu["pasta"] == os.path.join(koine_home["home"], "koine")


def test_instalar_no_windows_com_desktop_managed_false_nao_fecha_mas_segue(
        monkeypatch, tmp_path, koine_home):
    """Desfecho CORRIGIDO pela revisão dev-10 do plano (achado 1,
    25/09/2026): quando desktopManaged lê False com o app já rodando e a
    config mudou, o orquestrador NUNCA chama encerrar() — pré-checa o
    campo antes — avisa e SEGUE a sequência. O app continua rodando
    (esta_rodando() já True), então abrir() nunca precisa disparar; o
    daemon, presumivelmente de pé com a config antiga, responde
    normalmente e o workspace é garantido do mesmo jeito."""
    monkeypatch.setenv("HOME", koine_home["home"])
    chamadas, garantiu = _costura_feliz_windows(
        monkeypatch, tmp_path, config_mudou=True, ja_rodando=True,
        desktop_managed=False)

    rc = _instalar(koine_home)

    assert rc == 0
    assert chamadas["encerrou"] is False  # pré-check cortou antes de chamar
    assert chamadas["abriu"] is False  # app já rodando — não precisa abrir
    assert garantiu["pasta"] == os.path.join(koine_home["home"], "koine")


def test_instalar_com_daemon_no_ar_mas_garantir_falha_nao_derruba_instalador(
        monkeypatch, tmp_path, koine_home):
    """Achado da revisão dev-10 do plano, 22/09/2026: `garantir()` pode
    levantar PaseoIndisponivel (daemon caiu entre aguardar_daemon() e a
    chamada) — o instalador avisa e segue, nunca traceback cru."""
    monkeypatch.setenv("HOME", koine_home["home"])
    chamadas, _ = _costura_feliz(monkeypatch, tmp_path)

    def fake_garantir(pasta, titulo=""):
        raise paseo_workspace.PaseoIndisponivel("paseo workspace create falhou")
    monkeypatch.setattr(paseo_workspace, "garantir", fake_garantir)

    rc = _instalar(koine_home)

    assert rc == 0
