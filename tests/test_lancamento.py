import os

from koine.adapters import claude, codex
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento


def _cm(tmp_path, **kw):
    def w(n, t):
        p = str(tmp_path / n)
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
        return p
    base = dict(usuario_path=w("u.md", "# U\nx"), koine_path=w("k.md", "# K\nx"),
                agente_path=w("a.md", "# A\nx"), escopo_path=w("e.md", "# E\nx"),
                indice_paths=[], contexto_path=w("c.md", "# C\nx"),
                pasta_abs=str(tmp_path))
    base.update(kw)
    return ContextoMontado(**base)


def test_claude_renderiza_lancamento(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    lanc = claude.renderizar(_cm(tmp_path))
    assert isinstance(lanc, Lancamento)
    # a pasta não recebe nada: o CLAUDE.md vive no bundle do cache
    assert lanc.arquivos_working_dir == {}
    (destino,) = lanc.arquivos_externos
    assert os.path.basename(destino) == "CLAUDE.md"
    assert lanc.extra_args[0].startswith("--add-dir=")
    assert lanc.env_vars["CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD"] == "1"


def test_codex_lancamento_tem_extra_args(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    lanc = codex.renderizar(_cm(tmp_path, escopo_path="", contexto_path="", bootstrap=True))
    assert lanc.arquivos_working_dir == {}
    (arquivo,) = lanc.arquivos_externos
    assert os.path.basename(arquivo) == "AGENTS.md"
    # a constante do módulo continua indo, e o valor dinâmico compõe com ela
    assert lanc.extra_args[:2] == ["-c", "project_doc_max_bytes=1048576"]
    assert lanc.extra_args[2:] == ["-c", f"model_instructions_file={arquivo}"]
