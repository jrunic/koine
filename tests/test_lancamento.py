from koine.lancamento import Lancamento
from koine.contexto import ContextoMontado
from koine.adapters import claude, codex


def _cm():
    return ContextoMontado(usuario_path="/u.md", koine_path="/k.md", agente_path="/a.md",
                           escopo_path="/e.md", indice_paths=[], contexto_path="/c.md")


def test_claude_renderiza_lancamento():
    lanc = claude.renderizar(_cm())
    assert isinstance(lanc, Lancamento)
    assert "CLAUDE.md" in lanc.arquivos_working_dir
    assert lanc.arquivos_working_dir["CLAUDE.md"].splitlines()[1] == "# CLAUDE.md"
    assert lanc.extra_args == []


def test_codex_lancamento_tem_extra_args(tmp_path):
    def w(n, t):
        p = str(tmp_path / n); open(p, "w").write(t); return p
    cm = ContextoMontado(usuario_path=w("u.md", "# U\nx"), koine_path=w("k.md", "# K\nx"),
                         agente_path=w("hermes.md", "# H\nx"), escopo_path="",
                         indice_paths=[], contexto_path="", bootstrap=True)
    lanc = codex.renderizar(cm)
    assert "AGENTS.md" in lanc.arquivos_working_dir
    assert lanc.extra_args == ["-c", "project_doc_max_bytes=1048576"]
