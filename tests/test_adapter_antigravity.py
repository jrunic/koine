import os

from koine.adapters import antigravity, claude
from koine.contexto import ContextoMontado


def _cm(tmp_path, **kw):
    def w(n, t):
        p = str(tmp_path / n)
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
        return p
    base = dict(usuario_path=w("u.md", "# U\nBio."), koine_path=w("k.md", "# K\nManual."),
                agente_path=w("a.md", "# A\nPersona."), escopo_path=w("e.md", "# E\nRegras."),
                indice_paths=[w("kn-indice-universal.md", "# I\nEntradas.")],
                contexto_path=w("c.md", "# C\nSessão."), pasta_abs=str(tmp_path))
    base.update(kw)
    return ContextoMontado(**base)


def _unico(lanc):
    """Camada raw-unit: título e estrutura do adapter só aparecem no output CRU.
    O e2e normalizado não os vê — não colapsar um no outro."""
    (caminho,) = lanc.arquivos_externos
    return caminho, lanc.arquivos_externos[caminho]


def test_antigravity_arquivo_e_gemini(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    assert antigravity.ARQUIVO == "GEMINI.md"
    assert claude.ARQUIVO == "CLAUDE.md"
    agy_path, _ = _unico(antigravity.renderizar(_cm(tmp_path)))
    cla_path, _ = _unico(claude.renderizar(_cm(tmp_path)))
    assert os.path.basename(agy_path) == "GEMINI.md"
    assert os.path.basename(cla_path) == "CLAUDE.md"
    # bundles SEPARADOS: mesmo slot em categorias diferentes, senão um cliente
    # sobrescreveria o arquivo do outro
    assert os.path.dirname(agy_path) != os.path.dirname(cla_path)


def test_antigravity_render_titulo_e_camadas(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    _, out = _unico(antigravity.renderizar(_cm(tmp_path)))
    linhas = out.splitlines()
    assert linhas[0] == "<!-- gerado por kn-agente -->"
    assert linhas[1] == "# Sessão Koine — Antigravity"
    # o título é a divergência estrutural; as camadas são as mesmas do claude
    _, cla = _unico(claude.renderizar(_cm(tmp_path)))
    for secao in ("## Usuário", "## Koine", "## Agente", "## Escopo",
                  "## Referências — universal"):
        assert secao in out and secao in cla
    # conteúdo INLINE, nunca @path: fora da pasta o import não expande
    assert "@" + str(tmp_path) not in out


def test_antigravity_bootstrap_titulo(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    cm = _cm(tmp_path, bootstrap=True, usuario_path="", escopo_path="", indice_paths=[])
    _, out = _unico(antigravity.renderizar(cm))
    assert out.splitlines()[1] == "# Sessão Koine — Antigravity"
    assert "## Escopo" not in out
    assert "## Instruções desta sessão" in out
