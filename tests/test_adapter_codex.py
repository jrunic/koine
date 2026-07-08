import os
from koine.contexto import ContextoMontado
from koine.adapters import codex


def _cm(tmp_path):
    def w(nome, txt):
        p = str(tmp_path / nome); open(p, "w").write(txt); return p
    return ContextoMontado(
        usuario_path=w("u.md", "---\nid: 1\n---\n# Walter\nBio."),
        koine_path=w("k.md", "# Koine\nManual."),
        agente_path=w("hermes.md", "# Hermes\nPersona."),
        escopo_path=w("e.md", "# Escopo\nRegras."),
        indice_paths=[w("kn-indice-universal.md", "# Índice\nEntradas.")],
        contexto_path=w("CONTEXTO.md", "---\nescopo: x\n---\n# Ctx\nSessão."))


def test_codex_arquivo_e_extra_args():
    assert codex.ARQUIVO == "AGENTS.md"
    assert codex.EXTRA_ARGS == ["-c", "project_doc_max_bytes=1048576"]


def test_codex_render_inline_e_prosa(tmp_path):
    out = codex.renderizar(_cm(tmp_path)).arquivos_working_dir["AGENTS.md"]
    assert out.startswith("<!-- gerado por kn-agente -->\n")
    assert "# Sessão Koine — Codex" in out
    assert "## Usuário" in out and "Bio." in out           # conteúdo INLINE, não @path
    assert "@" + str(tmp_path) not in out                   # não referencia por @path
    assert "## Referências — universal" in out
    assert "## Instruções desta sessão" in out
    assert "kn-codex hermes ." in out                        # dica de regeneração
    assert out.endswith("\n")


def test_codex_bootstrap_omite_escopo(tmp_path):
    cm = _cm(tmp_path); cm.bootstrap = True
    out = codex.renderizar(cm).arquivos_working_dir["AGENTS.md"]
    assert "## Escopo" not in out and "## Referências" not in out
    assert "## Instruções desta sessão" in out
