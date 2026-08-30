"""Guardas das skills de acesso remoto (jd-task #703).

Prosa não tem compilador. Estes testes cobrem os três erros que a prosa destas
duas skills pode cometer sem ninguém perceber: expor o segredo de pareamento,
carregar uma cópia da matriz de clientes que envelhece, e inverter a ordem que
decide quase 1 GB de download.
"""
import pathlib

import pytest

VAULT = pathlib.Path(__file__).resolve().parent.parent / "vault" / "habilidades"
SKILLS_PASEO = ["kn-04-conecta-o-paseo", "kn-14-organiza-workspaces"]


def _texto(skill: str) -> str:
    return (VAULT / skill / "SKILL.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("skill", SKILLS_PASEO)
def test_a_skill_nao_manda_rodar_o_comando_de_pareamento(skill):
    """O link de pareamento equivale a senha, e o comando que o imprime não pode
    estar na skill — nem como exemplo. Escrito, alguém o roda numa sessão, e o
    segredo vai para o transcript.

    O pareamento é pela interface gráfica. Medido em 30/08/2026: por ferramenta
    o QR sequer renderiza ("terminal width could not be detected"), então nem
    funcionaria — a razão de segurança e a razão prática apontam para o mesmo
    lugar.
    """
    texto = _texto(skill)
    assert "daemon pair" not in texto, f"{skill}: cita o comando que imprime o link"
    assert "paseo onboard" not in texto, f"{skill}: `onboard` também imprime pareamento"


@pytest.mark.parametrize("skill", SKILLS_PASEO)
def test_a_skill_le_a_matriz_em_vez_de_repetir(skill):
    """A skill não pode carregar a tabela de quem tem rota: cópia envelhece
    sozinha, e o sintoma é um provider que abre sessão sem contexto e sem erro.

    O que se proíbe é a TABELA, não a palavra. Citar um cliente em prosa é
    legítimo — "se você usa o Claude Code" precisa ser dito. O que não pode é a
    associação cliente→`extends`, que é exatamente o que muda quando entra
    cliente novo. Um teste que proibisse o nome seria teste sem poder: falharia
    em prosa correta e passaria numa tabela escrita de outro jeito.
    """
    texto = _texto(skill)
    for proibido in ('extends": "claude', 'extends": "copilot', 'extends": "acp',
                     "extends: claude", "extends: copilot", "extends: acp"):
        assert proibido not in texto, f"{skill}: repete a matriz ({proibido})"


def test_so_a_skill_de_conexao_precisa_ler_a_matriz():
    """Quem escreve provider é a de conexão; a de organização não toca nisso.

    Exigir a leitura das duas seria teste sem poder na segunda — e forçaria a
    prosa a citar um comando que ela não usa, só para o teste passar. A proibição
    de repetir a tabela vale para as duas; a obrigação de ler, só para uma.
    """
    assert "paseo-info" in _texto("kn-04-conecta-o-paseo"), \
        "kn-04: não lê a matriz do Koine"


def test_a_skill_de_conexao_manda_configurar_antes_de_abrir():
    """A ordem decide 631 MB contra 1,6 GB.

    O daemon sobe quando o aplicativo abre, e baixa os modelos que a
    configuração pedir. Configurar depois **baixa outro** modelo em vez de
    trocar — medido em 30/08/2026 numa instalação limpa, que trouxe o modelo de
    ditado em inglês mais o de fala, 984 MB somados.
    """
    texto = _texto("kn-04-conecta-o-paseo").lower()
    assert "não abra" in texto or "nao abra" in texto, \
        "kn-04: falta o passo de NÃO abrir o app antes de configurar"
    assert "parakeet-tdt-0.6b-v3-int8" in texto, "kn-04: falta o modelo multilíngue"
    assert "voicemode" in texto, "kn-04: falta desligar o modo de voz"


def test_a_skill_de_conexao_avisa_o_que_nao_funciona():
    """Descobrir depois é pior. Os dois limites são nomeados na spec como coisa
    que o usuário precisa ouvir ANTES: os clientes sem rota, e a fala que não
    existe em português com o provedor gratuito."""
    texto = _texto("kn-04-conecta-o-paseo").lower()
    assert "codex" in texto, "kn-04: não nomeia o cliente sem rota"
    assert "antigravity" in texto, "kn-04: não nomeia o cliente sem rota"


def test_a_skill_de_organizacao_aponta_a_de_conexao():
    """A ordem entre as duas importa na primeira vez. Rodar a de organização sem
    o Paseo configurado tem que dizer isso, não falhar."""
    assert "kn-04" in _texto("kn-14-organiza-workspaces"), \
        "kn-14: não manda fazer a conexão antes"


def test_a_skill_de_conexao_desliga_o_relay_explicitamente():
    """Omitir a chave de relay EXPÕE a máquina, ao contrário do que a doc diz.

    Medido em 30/08/2026 na mesma máquina, mudando só a chave: ausente, o
    serviço conecta ao relay e fica alcançável pela internet; `enabled: false`,
    não conecta. Quem decide expor é o usuário, na tela do aplicativo — nunca a
    skill por omissão.
    """
    texto = _texto("kn-04-conecta-o-paseo")
    assert '"relay"' in texto, "kn-04: não escreve a chave de relay"
    assert '"enabled": false' in texto, "kn-04: não desliga o relay explicitamente"


def test_a_skill_de_conexao_exige_caminho_absoluto_do_wrapper():
    """O serviço do Paseo roda com ambiente mínimo, e a pasta de programas do
    usuário não está no caminho de busca dele.

    Medido em 30/08/2026: a skill escreveu o nome puro do wrapper no macOS (e o
    caminho absoluto no Windows — a mesma skill, escolhas diferentes), e os seis
    providers ficaram `Unavailable` com `Resolved path: not found`. Sessão aberta
    do celular não subiria.

    É o terceiro defeito da mesma forma no mesmo dia: a skill deixou uma decisão
    aberta, o agente escolheu diferente em cada máquina, e uma das escolhas
    quebra em silêncio.
    """
    texto = _texto("kn-04-conecta-o-paseo")
    assert "ABSOLUTO" in texto or "absoluto" in texto, \
        "kn-04: não exige o caminho absoluto do wrapper"
    assert "command -v" in texto, "kn-04: não diz como descobrir o caminho real"
