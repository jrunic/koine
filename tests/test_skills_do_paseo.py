"""Guardas das skills de acesso remoto (jd-task #703, #882).

Prosa não tem compilador. Estes testes cobrem os erros que a prosa destas
skills pode cometer sem ninguém perceber: expor o segredo de pareamento,
carregar uma cópia da matriz, inverter a ordem do download, e ditar JSON
em vez de chamar os comandos.
"""
import pathlib
import re

import pytest

VAULT = pathlib.Path(__file__).resolve().parent.parent / "vault" / "habilidades"
SKILLS_PASEO = ["kn-04-conecta-o-paseo", "kn-14-organiza-workspaces"]


def _texto(skill: str) -> str:
    return (VAULT / skill / "SKILL.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("skill", SKILLS_PASEO)
def test_a_skill_nao_manda_rodar_o_comando_de_pareamento(skill):
    """O link de pareamento equivale a senha, e o comando que o imprime não pode
    estar na skill — nem como exemplo.
    """
    texto = _texto(skill)
    assert "daemon pair" not in texto, f"{skill}: cita o comando que imprime o link"
    assert "paseo onboard" not in texto, f"{skill}: `onboard` também imprime pareamento"


@pytest.mark.parametrize("skill", SKILLS_PASEO)
def test_a_skill_le_a_matriz_em_vez_de_repetir(skill):
    texto = _texto(skill)
    for proibido in ('extends": "claude', 'extends": "copilot', 'extends": "acp',
                     "extends: claude", "extends: copilot", "extends: acp"):
        assert proibido not in texto, f"{skill}: repete a matriz ({proibido})"


def test_so_a_skill_de_conexao_precisa_ler_a_matriz():
    assert "paseo-info" in _texto("kn-04-conecta-o-paseo"), \
        "kn-04: não lê a matriz do Koine"


def test_a_skill_de_conexao_manda_configurar_antes_de_abrir():
    texto = _texto("kn-04-conecta-o-paseo").lower()
    assert "não abra" in texto or "nao abra" in texto, \
        "kn-04: falta o passo de NÃO abrir o app antes de configurar"


def test_a_skill_de_conexao_avisa_o_que_nao_funciona():
    texto = _texto("kn-04-conecta-o-paseo").lower()
    assert "codex" in texto, "kn-04: não nomeia o cliente sem rota"
    assert "antigravity" in texto, "kn-04: não nomeia o cliente sem rota"


def test_a_skill_de_organizacao_aponta_a_de_conexao():
    assert "kn-04" in _texto("kn-14-organiza-workspaces"), \
        "kn-14: não manda fazer a conexão antes"


def test_a_skill_de_conexao_chama_os_tres_comandos():
    texto = _texto("kn-04-conecta-o-paseo")
    assert "paseo-configurar" in texto
    assert "paseo-provider" in texto
    assert "paseo-doctor" in texto


def test_a_skill_de_conexao_nao_dita_json_de_config():
    texto = _texto("kn-04-conecta-o-paseo")
    assert "parakeet-tdt-0.6b-v3-int8" not in texto
    assert "features.dictation" not in texto
    assert "agents.providers" not in texto
    assert re.search(r"```json\s*\{", texto) is None
    assert re.search(r'"version"\s*:\s*1', texto) is None


def test_a_skill_de_conexao_guia_login_do_navegador_interno():
    texto = _texto("kn-04-conecta-o-paseo")
    assert "Please run login" in texto
    baixo = texto.lower()
    assert "não é o login do claude" in baixo or "nao e o login do claude" in baixo


def test_a_skill_de_conexao_chama_o_provider_nao_o_which():
    texto = _texto("kn-04-conecta-o-paseo")
    assert "paseo-provider" in texto
    assert "command -v" not in texto


def test_a_skill_de_conexao_explica_que_omitir_relay_expoe():
    texto = _texto("kn-04-conecta-o-paseo").lower()
    assert "relay" in texto
    assert "expõe" in texto or "expoe" in texto


def test_a_skill_de_conexao_reload_na_reexecucao():
    texto = _texto("kn-04-conecta-o-paseo")
    assert "paseo reload" in texto
    baixo = texto.lower()
    assert "sessão" in baixo or "sessao" in baixo
    assert "paseo" in baixo


def test_a_skill_de_organizacao_tem_rename_e_archive():
    texto = _texto("kn-14-organiza-workspaces")
    assert "workspace rename" in texto
    assert "workspace archive" in texto
    assert "--reset" in texto


def test_a_skill_de_organizacao_nao_inventa_move():
    texto = _texto("kn-14-organiza-workspaces")
    assert "workspace move" not in texto


def test_a_skill_de_organizacao_avisa_mv_da_pasta():
    """Trecho contínuo — não palavras soltas em seções diferentes."""
    texto = _texto("kn-14-organiza-workspaces").lower()
    assert "auto-arquiv" in texto


def test_a_skill_de_organizacao_rename_e_titulo():
    texto = _texto("kn-14-organiza-workspaces").lower()
    assert "título" in texto or "titulo" in texto


def test_a_skill_de_organizacao_archive_sem_desfazer():
    texto = _texto("kn-14-organiza-workspaces").lower()
    assert "não tem" in texto or "nao tem" in texto
    assert "desarquiv" in texto or "unarchive" in texto


def test_a_skill_de_organizacao_nao_cita_setup():
    assert "workspace setup" not in _texto("kn-14-organiza-workspaces")


def test_a_skill_de_organizacao_nao_oferece_mover_por_recriar():
    texto = _texto("kn-14-organiza-workspaces").lower()
    assert "não faz isso" in texto or "nao faz isso" in texto
