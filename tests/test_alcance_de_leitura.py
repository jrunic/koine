"""As raízes que a sessão precisa alcançar, e o que cada adapter faz com elas.

Nove das catorze skills mandam ler `~/.config/koine/` e o vault por caminho
absoluto. Três de cinco clientes NEGAM essa leitura fora do diretório de
trabalho — medido cliente a cliente em 11/09/2026 (jd-task #887). No terminal o
usuário aprova e ninguém percebe; no canal do orquestrador não há quem aprove, e
a skill trava ou inventa formato.
"""
import json
import os

import pytest

from koine import adapters, paths, render
from koine.contexto import ContextoMontado


def test_raizes_sao_config_e_vault(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    raizes = render.raizes_de_leitura()

    assert raizes == (paths.config_dir(), paths.vault_dir())


def test_raizes_sao_diretorios_e_nao_arquivos(tmp_path, monkeypatch):
    """`--add-dir` recebe diretório. Raiz que aponte para arquivo (o KOINE.md,
    por exemplo) é ignorada em silêncio pelo cliente."""
    monkeypatch.setenv("HOME", str(tmp_path))

    for r in render.raizes_de_leitura():
        assert not r.endswith(".md")


# O que cada cliente precisa, medido por execução em 11/09/2026 na bancada:
#   claude/agy/copilot → --add-dir por raiz     (os três leem depois disso)
#   opencode           → permission.external_directory com glob
#   codex              → NADA: já lê sem pedir permissão
POR_ADD_DIR = ("claude", "agy", "copilot")


@pytest.fixture
def cm(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    for nome in ("usuario.md", "KOINE.md", "hermes.md", "escopo.md", "CONTEXTO.md"):
        (tmp_path / nome).write_text(f"# {nome}", encoding="utf-8")
    pasta = tmp_path / "trab"
    pasta.mkdir()
    return ContextoMontado(
        usuario_path=str(tmp_path / "usuario.md"),
        koine_path=str(tmp_path / "KOINE.md"),
        agente_path=str(tmp_path / "hermes.md"),
        escopo_path=str(tmp_path / "escopo.md"),
        contexto_path=str(tmp_path / "CONTEXTO.md"),
        pasta_abs=str(pasta),
    )


@pytest.mark.parametrize("cliente", POR_ADD_DIR)
def test_adapter_libera_as_raizes_por_add_dir(cliente, cm):
    lanc = adapters.get(cliente).renderizar(cm)

    for raiz in render.raizes_de_leitura():
        assert f"--add-dir={raiz}" in (lanc.extra_args or []), (
            f"{cliente} não libera {raiz}: a skill que ler de lá vai travar "
            "onde não houver quem aprove")


def test_opencode_libera_as_raizes_por_permissao(cm):
    lanc = adapters.get("opencode").renderizar(cm)
    cfg_path = [p for p in lanc.arquivos_externos if p.endswith(".json")][0]
    cfg = json.loads(lanc.arquivos_externos[cfg_path])

    externo = cfg["permission"]["external_directory"]
    for raiz in render.raizes_de_leitura():
        assert externo.get(f"{raiz.replace(os.sep, '/')}/*") == "allow"


def test_codex_nao_recebe_add_dir(cm):
    """Medido: o codex lê sem pedir permissão. Flag por simetria é código que
    ninguém exercita — e 'não recebe' também é contrato."""
    lanc = adapters.get("codex").renderizar(cm)

    assert not any(a.startswith("--add-dir") for a in (lanc.extra_args or []))
