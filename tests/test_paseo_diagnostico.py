"""Verificações do `koine paseo-doctor` (jd-task #879).

Toda medição desta suíte parte de uma árvore montada em tmp_path e de uma
costura sobre a CLI do Paseo. Nenhum teste exige o Paseo instalado.
"""
import json
import os

import pytest

from koine import paseo_diagnostico as pd


def _monta_home(tmp_path, config: dict | str | None):
    """Árvore mínima do Paseo em tmp_path.

    `config` aceita dict (gravado como JSON), str (gravado cru, para o caso de
    JSON inválido) ou None (arquivo ausente).
    """
    home = tmp_path / ".paseo"
    home.mkdir(parents=True, exist_ok=True)
    if config is not None:
        bruto = config if isinstance(config, str) else json.dumps(config)
        (home / "config.json").write_text(bruto, encoding="utf-8")
    return str(home)


def test_home_vem_da_variavel_de_ambiente(tmp_path, monkeypatch):
    monkeypatch.setenv("PASEO_HOME", str(tmp_path / "outro"))
    assert pd.home_do_paseo() == str(tmp_path / "outro")


def test_home_cai_no_default_sem_variavel(monkeypatch):
    monkeypatch.delenv("PASEO_HOME", raising=False)
    monkeypatch.setenv("HOME", "/tmp/casa-falsa")
    assert pd.home_do_paseo() == os.path.join("/tmp/casa-falsa", ".paseo")


def test_config_ausente_e_erro(tmp_path):
    home = _monta_home(tmp_path, None)
    cfg, v = pd.ler_config(home)
    assert cfg is None
    assert v.situacao == pd.ERRO
    assert v.id == "config.legivel"


def test_config_invalido_e_erro_e_diz_que_e_sintaxe(tmp_path):
    home = _monta_home(tmp_path, "{isto nao e json")
    cfg, v = pd.ler_config(home)
    assert cfg is None
    assert v.situacao == pd.ERRO
    assert v.dado["motivo"] == "invalido"


def test_config_valido_e_ok(tmp_path):
    home = _monta_home(tmp_path, {"version": 1})
    cfg, v = pd.ler_config(home)
    assert cfg == {"version": 1}
    assert v.situacao == pd.OK


def test_busca_distingue_ausente_de_false():
    cfg = {"daemon": {"browserTools": {"enabled": False}}}
    assert pd.busca(cfg, "daemon.browserTools.enabled") is False
    assert pd.busca(cfg, "daemon.mcp.injectIntoAgents") is pd.AUSENTE


def test_chave_do_canal_ausente_e_erro():
    v = pd.verificar_chave_do_canal({}, "daemon.browserTools.enabled")
    assert v.situacao == pd.ERRO
    assert v.dado["estado"] == "ausente"


def test_chave_do_canal_desligada_e_erro_com_estado_proprio():
    cfg = {"daemon": {"browserTools": {"enabled": False}}}
    v = pd.verificar_chave_do_canal(cfg, "daemon.browserTools.enabled")
    assert v.situacao == pd.ERRO
    assert v.dado["estado"] == "desligada"


def test_chave_do_canal_ligada_e_ok():
    cfg = {"daemon": {"browserTools": {"enabled": True}}}
    assert pd.verificar_chave_do_canal(
        cfg, "daemon.browserTools.enabled").situacao == pd.OK


def test_relay_ausente_e_erro_porque_expoe_a_maquina():
    v = pd.verificar_relay({})
    assert v.situacao == pd.ERRO


@pytest.mark.parametrize("ligado", [True, False])
def test_relay_presente_nunca_reprova(ligado):
    cfg = {"daemon": {"relay": {"enabled": ligado}}}
    v = pd.verificar_relay(cfg)
    assert v.situacao == pd.OK
    assert v.dado["habilitado"] is ligado


def test_voz_configurada_e_ok():
    cfg = {"daemon": {"voice": {"sttProvider": "parakeet"}}}
    v = pd.verificar_voz(cfg)
    assert v.situacao == pd.OK
    assert v.dado["provedor"] == "parakeet"


def test_voz_ausente_e_aviso_nunca_erro():
    """A máquina funciona sem voz. Reprovar aqui seria reprovar uma escolha."""
    v = pd.verificar_voz({})
    assert v.situacao == pd.AVISO


def test_rodar_paseo_devolve_none_quando_a_cli_nao_existe(monkeypatch):
    from koine import paseo_ambiente as amb
    # sem executável no PATH NEM no local padrão — costura no resolvedor,
    # porque o fallback de instalação padrão é caminho legítimo desde a
    # spec 20260915
    monkeypatch.setattr(amb, "resolver_executavel", lambda n: None)
    assert pd._rodar_paseo(["status"]) is None


def test_rodar_paseo_devolve_none_quando_a_cli_falha(monkeypatch):
    """Saída não-zero é "não deu para perguntar", não "a resposta é vazia"."""
    from koine import paseo_ambiente as amb
    monkeypatch.setattr(amb, "resolver_executavel",
                        lambda n: amb.Executavel("/usr/bin/paseo", "path"))
    monkeypatch.setattr(
        amb, "executar",
        lambda *a, **k: type("R", (), {"returncode": 1, "stdout": "lixo"})())
    assert pd._rodar_paseo(["status"]) is None


_STATUS_DE_PE = (
    "Local Daemon           running\n"
    "Listen                 127.0.0.1:6767\n"
    "Daemon Version         0.8.0\n"
)


def test_servico_de_pe_e_ok(monkeypatch):
    monkeypatch.setattr(pd, "_rodar_paseo", lambda *a, **k: _STATUS_DE_PE)
    v = pd.verificar_servico({"daemon": {"listen": "127.0.0.1:6767"}})
    assert v.situacao == pd.OK


def test_porta_fora_do_padrao_nao_reprova_por_si(monkeypatch):
    """A 6767 é o valor DESTA máquina, não uma constante do produto."""
    status = _STATUS_DE_PE.replace("6767", "9999")
    monkeypatch.setattr(pd, "_rodar_paseo", lambda *a, **k: status)
    v = pd.verificar_servico({"daemon": {"listen": "127.0.0.1:9999"}})
    assert v.situacao == pd.OK
    assert v.dado["listen"] == "127.0.0.1:9999"


def test_servico_fora_do_ar_e_erro(monkeypatch):
    monkeypatch.setattr(pd, "_rodar_paseo", lambda *a, **k: None)
    v = pd.verificar_servico({"daemon": {"listen": "127.0.0.1:6767"}})
    assert v.situacao == pd.ERRO
    assert v.dado["motivo"] == "cli-ausente"


def _costura_de_versao(monkeypatch, app: str, daemon: str | None):
    def fake(args, **k):
        if args[:1] == ["--version"]:
            return f"{app}\n"
        if args[:1] == ["status"]:
            linha = f"Daemon Version         {daemon}\n" if daemon else ""
            return "Local Daemon           running\n" + linha
        return ""
    monkeypatch.setattr(pd, "_rodar_paseo", fake)


def test_versoes_iguais_e_ok(monkeypatch):
    _costura_de_versao(monkeypatch, "0.8.0", "0.8.0")
    assert pd.verificar_versoes().situacao == pd.OK


def test_daemon_atras_do_aplicativo_e_erro(monkeypatch):
    _costura_de_versao(monkeypatch, "0.8.0", "0.7.2")
    v = pd.verificar_versoes()
    assert v.situacao == pd.ERRO
    assert v.dado == {"aplicativo": "0.8.0", "daemon": "0.7.2"}


def test_daemon_sem_versao_publicada_e_aviso(monkeypatch):
    _costura_de_versao(monkeypatch, "0.8.0", None)
    assert pd.verificar_versoes().situacao == pd.AVISO


def _agente(home, pasta, nome, criado_em, com_mcp, mtime=None):
    d = os.path.join(home, "agents", pasta)
    os.makedirs(d, exist_ok=True)
    md = {"cwd": "/x", "provider": "claude"}
    if com_mcp:
        md["mcpServers"] = {"paseo": {"command": "paseo"}}
    caminho = os.path.join(d, f"{nome}.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump({"createdAt": criado_em, "persistence": {"metadata": md}}, f)
    if mtime is not None:
        os.utime(caminho, (mtime, mtime))
    return caminho


LIGADA = {"daemon": {"mcp": {"injectIntoAgents": True}}}


def test_arvore_de_agentes_vazia_nao_reprova(tmp_path):
    home = _monta_home(tmp_path, LIGADA)
    v = pd.verificar_mcp_nos_agentes(LIGADA, home)
    assert v.situacao == pd.OK
    assert v.dado["estado"] == "sem-agentes"


def test_nenhum_agente_com_mcp_e_aviso_nao_erro(tmp_path):
    home = _monta_home(tmp_path, LIGADA)
    _agente(home, "p1", "a", "2026-09-12T10:00:00.000Z", com_mcp=False)
    v = pd.verificar_mcp_nos_agentes(LIGADA, home)
    assert v.situacao == pd.AVISO
    assert v.dado["estado"] == "sem-fronteira"


def test_agente_posterior_a_fronteira_sem_mcp_e_erro(tmp_path):
    home = _monta_home(tmp_path, LIGADA)
    _agente(home, "p1", "pioneiro", "2026-08-25T17:08:00.000Z", com_mcp=True)
    _agente(home, "p2", "novo", "2026-09-12T10:00:00.000Z", com_mcp=False)
    v = pd.verificar_mcp_nos_agentes(LIGADA, home)
    assert v.situacao == pd.ERRO
    assert v.dado["sem_mcp"] == 1


def test_agente_anterior_a_fronteira_sem_mcp_nao_reprova(tmp_path):
    home = _monta_home(tmp_path, LIGADA)
    _agente(home, "p1", "veterano", "2026-08-24T16:49:32.948Z", com_mcp=False)
    _agente(home, "p2", "pioneiro", "2026-08-25T17:08:00.000Z", com_mcp=True)
    v = pd.verificar_mcp_nos_agentes(LIGADA, home)
    assert v.situacao == pd.OK
    assert v.dado["anteriores_a_fronteira"] == 1


def test_createdat_manda_e_a_data_do_arquivo_nao(tmp_path):
    home = _monta_home(tmp_path, LIGADA)
    _agente(home, "p1", "veterano", "2026-08-24T16:49:32.948Z",
            com_mcp=False, mtime=1789000000)
    _agente(home, "p2", "pioneiro", "2026-08-25T17:08:00.000Z",
            com_mcp=True, mtime=1)
    assert pd.verificar_mcp_nos_agentes(LIGADA, home).situacao == pd.OK


def test_chave_desligada_nao_cobra_mcp(tmp_path):
    desligada = {"daemon": {"mcp": {"injectIntoAgents": False}}}
    home = _monta_home(tmp_path, desligada)
    _agente(home, "p1", "a", "2026-09-12T10:00:00.000Z", com_mcp=False)
    assert pd.verificar_mcp_nos_agentes(desligada, home).situacao == pd.OK


def _particao(base, nome, bytes_de_cookie):
    d = os.path.join(base, nome)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "Cookies"), "wb") as f:
        f.write(b"\0" * bytes_de_cookie)


LIGADO = {"daemon": {"browserTools": {"enabled": True}}}


def test_navegador_com_sessao_gravada_e_ok(tmp_path):
    base = tmp_path / "parts"
    _particao(str(base), "paseo-browser", 524288)
    v = pd.verificar_navegador(LIGADO, str(base))
    assert v.situacao == pd.OK
    assert v.dado["tem_sessao"] is True


def test_navegador_nunca_usado_para_login_e_aviso(tmp_path):
    base = tmp_path / "parts"
    _particao(str(base), "paseo-browser", 20480)
    v = pd.verificar_navegador(LIGADO, str(base))
    assert v.situacao == pd.AVISO
    assert v.dado["tem_sessao"] is False


def test_navegador_desligado_e_erro_sem_olhar_o_disco(tmp_path):
    desligado = {"daemon": {"browserTools": {"enabled": False}}}
    v = pd.verificar_navegador(desligado, str(tmp_path / "nao-existe"))
    assert v.situacao == pd.ERRO


def test_particao_nao_encontrada_nao_afirma_que_faltou_login(tmp_path):
    v = pd.verificar_navegador(LIGADO, str(tmp_path / "nao-existe"))
    assert v.situacao == pd.AVISO
    assert v.dado["tem_sessao"] is None
    assert v.dado["estado"] == "nao-medido"


def test_particao_vazia_afirma_que_faltou_login(tmp_path):
    base = tmp_path / "parts"
    _particao(str(base), "paseo-browser", 20480)
    v = pd.verificar_navegador(LIGADO, str(base))
    assert v.dado["estado"] == "sem-login"


def test_base_de_particoes_e_none_fora_das_plataformas_medidas(monkeypatch):
    monkeypatch.setattr(pd.sys, "platform", "sunos5")
    assert pd.particoes_do_navegador() is None


def _cfg_com_providers(*nomes):
    return {"agents": {"providers": {n: {"extends": "claude"} for n in nomes}}}


def test_zero_providers_do_koine_nao_e_erro(monkeypatch):
    monkeypatch.setattr(pd, "_prescritos", lambda: ["kn-claude", "kn-codex"])
    v = pd.verificar_providers(_cfg_com_providers("jd-leia"))
    assert v.situacao == pd.OK
    assert v.dado["estado"] == "nao-adotado"


def test_configuracao_parcial_e_erro(monkeypatch):
    monkeypatch.setattr(pd, "_prescritos", lambda: ["kn-claude", "kn-codex"])
    v = pd.verificar_providers(_cfg_com_providers("kn-claude"))
    assert v.situacao == pd.ERRO
    assert v.dado["faltando"] == ["kn-codex"]


def test_todos_os_prescritos_presentes_e_ok(monkeypatch):
    monkeypatch.setattr(pd, "_prescritos", lambda: ["kn-claude", "kn-codex"])
    monkeypatch.setattr(pd, "_disponiveis", lambda: ({"kn-claude", "kn-codex"}, set()))
    v = pd.verificar_providers(_cfg_com_providers("kn-claude", "kn-codex"))
    assert v.situacao == pd.OK
    assert v.dado["estado"] == "completo"


def test_presente_no_config_e_indisponivel_no_servico_e_erro(monkeypatch):
    monkeypatch.setattr(pd, "_prescritos", lambda: ["kn-claude", "kn-codex"])
    monkeypatch.setattr(pd, "_disponiveis", lambda: ({"kn-claude"}, set()))
    v = pd.verificar_providers(_cfg_com_providers("kn-claude", "kn-codex"))
    assert v.situacao == pd.ERRO
    assert v.dado["indisponiveis"] == ["kn-codex"]


def test_servico_mudo_nao_transforma_silencio_em_erro(monkeypatch):
    monkeypatch.setattr(pd, "_prescritos", lambda: ["kn-claude"])
    monkeypatch.setattr(pd, "_disponiveis", lambda: None)
    v = pd.verificar_providers(_cfg_com_providers("kn-claude"))
    assert v.situacao == pd.OK


def test_config_ilegivel_encerra_o_diagnostico(tmp_path, monkeypatch):
    monkeypatch.setenv("PASEO_HOME", _monta_home(tmp_path, None))
    verificacoes = pd.diagnosticar()
    assert len(verificacoes) == 1
    assert verificacoes[0].id == "config.legivel"


def test_codigo_de_saida_zero_sem_erro():
    assert pd.codigo_de_saida([
        pd.Verificacao("a", pd.OK, "x"),
        pd.Verificacao("b", pd.AVISO, "y"),
    ]) == 0


def test_codigo_de_saida_nao_zero_com_erro():
    assert pd.codigo_de_saida([
        pd.Verificacao("a", pd.OK, "x"),
        pd.Verificacao("b", pd.ERRO, "y"),
    ]) == 1


def test_aviso_sozinho_nunca_reprova():
    assert pd.codigo_de_saida([pd.Verificacao("a", pd.AVISO, "x")]) == 0


def test_cli_json_traz_um_item_por_verificacao(monkeypatch, capsys):
    monkeypatch.setattr(
        "koine.paseo_diagnostico.diagnosticar",
        lambda home=None: [pd.Verificacao("a.b", pd.OK, "tudo certo", {"x": 1})])
    from koine import cli
    assert cli.main(["paseo-doctor", "--json"]) == 0
    saida = json.loads(capsys.readouterr().out)
    assert saida == [{"id": "a.b", "situacao": "ok",
                      "mensagem": "tudo certo", "dado": {"x": 1}}]


def test_cli_sai_nao_zero_quando_ha_erro(monkeypatch, capsys):
    monkeypatch.setattr(
        "koine.paseo_diagnostico.diagnosticar",
        lambda home=None: [pd.Verificacao("a.b", pd.ERRO, "quebrou")])
    from koine import cli
    assert cli.main(["paseo-doctor"]) == 1
    assert "quebrou" in capsys.readouterr().out


def test_cli_tabela_marca_cada_situacao(monkeypatch, capsys):
    monkeypatch.setattr(
        "koine.paseo_diagnostico.diagnosticar",
        lambda home=None: [pd.Verificacao("a", pd.OK, "m1"),
                           pd.Verificacao("b", pd.AVISO, "m2"),
                           pd.Verificacao("c", pd.ERRO, "m3")])
    from koine import cli
    cli.main(["paseo-doctor"])
    linhas = capsys.readouterr().out.splitlines()
    assert sum(1 for l in linhas if "m1" in l or "m2" in l or "m3" in l) == 3


# --- CLI do Paseo pelo resolvedor de ambiente (spec 20260915) --------------

def test_rodar_paseo_usa_o_ambiente(monkeypatch):
    from koine import paseo_ambiente as amb
    chamadas = []

    def fake_executar(exe, args, **kw):
        chamadas.append((exe, args))
        return type("R", (), {"returncode": 0, "stdout": "ok"})()

    monkeypatch.setattr(amb, "resolver_executavel",
                        lambda n: amb.Executavel("/fora/do/path/paseo.cmd",
                                                 "fallback"))
    monkeypatch.setattr(amb, "executar", fake_executar)
    assert pd._rodar_paseo(["status"]) == "ok"
    assert chamadas[0] == ("/fora/do/path/paseo.cmd", ["status"])


def test_verifica_executaveis_aponta_diretorio_do_path(monkeypatch):
    from koine import paseo_ambiente as amb
    monkeypatch.setattr(amb, "resolver_executavel",
                        lambda n: amb.Executavel(
                            r"C:\Apps\Paseo\resources\bin\paseo.cmd",
                            "fallback") if n == "paseo" else None)
    v = pd.verificar_executaveis()
    assert v.situacao == pd.AVISO
    assert r"C:\Apps\Paseo\resources\bin" in v.mensagem
    assert "PATH" in v.mensagem


def test_verifica_executaveis_no_path_e_ok(monkeypatch):
    from koine import paseo_ambiente as amb
    monkeypatch.setattr(amb, "resolver_executavel",
                        lambda n: amb.Executavel("/usr/local/bin/paseo", "path"))
    v = pd.verificar_executaveis()
    assert v.situacao == pd.OK


def test_verifica_executaveis_ausente_e_erro_com_procurados(monkeypatch):
    from koine import paseo_ambiente as amb
    monkeypatch.setattr(amb, "resolver_executavel", lambda n: None)
    monkeypatch.setattr(amb, "pastas_padrao_do_paseo",
                        lambda: [r"C:\Apps\Paseo\resources\bin"])
    v = pd.verificar_executaveis()
    assert v.situacao == pd.ERRO
    assert r"C:\Apps\Paseo\resources\bin" in v.mensagem


# --- versão sem log de startup; provider desligado (medido em campo, 15/09) -

def test_versao_ignora_log_de_startup(monkeypatch):
    bruto = "Starting daemon...\nlistening on pipe\n0.8.0\n"
    monkeypatch.setattr(pd, "_rodar_paseo",
                        lambda a: bruto if a == ["--version"] else
                        "Daemon Version: 0.8.0\n")
    v = pd.verificar_versoes()
    assert v.situacao == pd.OK
    assert v.dado["aplicativo"] == "0.8.0"


def test_provider_prescrito_desligado_e_aviso_nunca_erro(monkeypatch):
    lista = json.dumps([
        {"provider": "kn-claude", "status": "disabled"},
        {"provider": "kn-claude-hermes", "status": "available"}])
    monkeypatch.setattr(pd, "_rodar_paseo",
                        lambda a: lista if a == ["provider", "ls", "--json"]
                        else None)
    cfg = {"agents": {"providers": {"kn-claude": {}, "kn-claude-hermes": {}}}}
    monkeypatch.setattr(pd, "_prescritos",
                        lambda: ["kn-claude", "kn-claude-hermes"])
    v = pd.verificar_providers(cfg)
    assert v.situacao == pd.AVISO
    assert v.dado["desligados"] == ["kn-claude"]
