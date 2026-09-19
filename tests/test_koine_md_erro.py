import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KOINE_MD = os.path.join(ROOT, "vault", "KOINE.md")


def _texto():
    with open(KOINE_MD, encoding="utf-8") as f:
        return f.read()


def test_koine_md_aponta_para_a_skill_de_erro():
    assert "kn-17-trata-erro" in _texto()


def test_koine_md_nao_vira_catalogo_de_erros():
    # Critério de sucesso da spec: "exatamente uma linha nova... nenhum
    # catálogo de erros específicos". Cada termo abaixo é sintoma de que
    # alguém colou um caso concreto aqui em vez de manter a instrução
    # genérica e deixar o catálogo em docs/referencias/erros-conhecidos.md.
    texto_min = _texto().lower()
    for termo_proibido in ("winerror", "unexpected server error", "pwsh.exe",
                           "codex-code-mode-host", "unicodeencodeerror"):
        assert termo_proibido not in texto_min, (
            f"KOINE.md ganhou um caso concreto ({termo_proibido!r}) — "
            "isso pertence a docs/referencias/erros-conhecidos.md"
        )


def test_koine_md_tem_no_maximo_uma_linha_a_mais_que_o_baseline():
    # Baseline medido em 19/09/2026, antes desta mudança: 43 linhas
    # (`wc -l vault/KOINE.md`). Depois desta task: 44. Se crescer mais que
    # isso, alguém colou instrução extra em vez de uma linha só.
    linhas = _texto().count("\n")
    assert linhas <= 44, f"KOINE.md tem {linhas} linhas — baseline+1 é 44"
