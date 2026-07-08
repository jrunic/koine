from koine.contexto import ContextoMontado
from koine.adapters import antigravity, claude


def _cm():
    return ContextoMontado(
        usuario_path="/u.md", koine_path="/k.md", agente_path="/a.md",
        escopo_path="/e.md", indice_paths=["/i1.md", "/i2.md"], contexto_path="/c.md")


def test_antigravity_arquivo_e_gemini():
    assert antigravity.ARQUIVO == "GEMINI.md"
    assert claude.ARQUIVO == "CLAUDE.md"


def test_antigravity_render_titulo_e_refs():
    out = antigravity.renderizar(_cm())
    linhas = out.splitlines()
    assert linhas[0] == "<!-- gerado por kn-agente -->"
    assert linhas[1] == "# GEMINI.md"
    # mesmas linhas @ref do claude (título é a única divergência estrutural)
    refs_agy = [l for l in linhas if l.startswith("@")]
    refs_cla = [l for l in claude.renderizar(_cm()).splitlines() if l.startswith("@")]
    assert refs_agy == refs_cla


def test_antigravity_bootstrap_titulo():
    cm = ContextoMontado(bootstrap=True, usuario_path="", koine_path="/k.md",
                         agente_path="/a.md", contexto_path="/c.md")
    out = antigravity.renderizar(cm)
    assert out.splitlines()[1] == "# GEMINI.md"
    assert "modo bootstrap" in out
    assert out.endswith("\n\n")
