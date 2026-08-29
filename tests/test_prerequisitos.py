import os

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


def test_opencode_em_arm64_avisa_da_tui_quebrada():
    achados = pre.avaliar(["opencode"], sonda=_sonda(SAUDAVEL), arquitetura="ARM64")
    assert [a.codigo for a in achados] == [pre.OPENCODE_TUI_ARM64]


def test_opencode_em_amd64_nao_avisa():
    assert pre.avaliar(["opencode"], sonda=_sonda(SAUDAVEL), arquitetura="AMD64") == []


def test_codex_sem_o_code_mode_host_e_instalacao_incompleta(tmp_path):
    # O `.exe.zip` traz três binários e NÃO traz o code-mode-host; sem ele o
    # codex falha fechado em toda ferramenta, com erro que parece limitação do
    # modelo. Medido em 28/08.
    (tmp_path / "codex.exe").write_text("")
    achados = pre.avaliar(["codex"], sonda=_sonda(SAUDAVEL),
                          pasta_codex=str(tmp_path))
    assert [a.codigo for a in achados] == [pre.CODEX_INCOMPLETO]


def test_codex_com_o_host_ao_lado_esta_completo(tmp_path):
    (tmp_path / "codex.exe").write_text("")
    (tmp_path / "codex-code-mode-host.exe").write_text("")
    assert pre.avaliar(["codex"], sonda=_sonda(SAUDAVEL),
                       pasta_codex=str(tmp_path)) == []


def test_codex_com_pasta_desconhecida_nao_acusa_nada(tmp_path):
    # Silêncio quando não dá para saber: acusar instalação boa de incompleta é
    # pior do que não acusar.
    assert pre.avaliar(["codex"], sonda=_sonda(SAUDAVEL), pasta_codex=None) == []


def test_pasta_do_codex_pelo_exe_no_path(tmp_path, monkeypatch):
    exe = tmp_path / "codex.exe"
    exe.write_text("")
    monkeypatch.setattr(pre.shutil, "which", lambda n: str(exe))
    assert pre.codex_dir() == str(tmp_path)


def test_pasta_do_codex_pelo_shim_cmd(tmp_path, monkeypatch):
    alvo = tmp_path / "app" / "bin"
    alvo.mkdir(parents=True)
    (alvo / "codex.exe").write_text("")
    shim = tmp_path / "codex.cmd"
    # O separador tem que ser o da PLATAFORMA: escrever `\` literal faz o
    # os.path.dirname do POSIX devolver a pasta errada, e o teste mede o meu
    # literal em vez do código.
    exe = os.path.join(str(alvo), "codex.exe")
    shim.write_text(f'@"{exe}" %*\n', encoding="utf-8")
    monkeypatch.setattr(pre.shutil, "which", lambda n: str(shim))
    assert pre.codex_dir() == str(alvo)


def test_pasta_do_codex_desconhecida_devolve_none(monkeypatch):
    monkeypatch.setattr(pre.shutil, "which", lambda n: None)
    assert pre.codex_dir() is None


def test_shim_ilegivel_devolve_none(tmp_path, monkeypatch):
    shim = tmp_path / "codex.cmd"
    shim.write_text("@echo nada aqui\n", encoding="utf-8")
    monkeypatch.setattr(pre.shutil, "which", lambda n: str(shim))
    assert pre.codex_dir() is None
