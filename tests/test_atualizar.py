# tests/test_atualizar.py
import hashlib
import pytest
from koine import atualizar


def test_versao_pinada_por_env(monkeypatch):
    monkeypatch.setenv("KOINE_VERSAO", "v0.9.9")
    assert atualizar.resolver_versao() == ("v0.9.9", "0.9.9")


def test_versao_pinada_sem_v(monkeypatch):
    monkeypatch.setenv("KOINE_VERSAO", "0.9.9")
    assert atualizar.resolver_versao() == ("v0.9.9", "0.9.9")


def test_versao_latest_github(monkeypatch):
    monkeypatch.delenv("KOINE_VERSAO", raising=False)

    class FakeResp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def geturl(self): return "https://github.com/jrunic/koine/releases/tag/v1.2.3"

    capturado = {}

    def fake_urlopen(req, timeout=30):
        capturado["ua"] = req.get_header("User-agent")
        return FakeResp()

    monkeypatch.setattr(atualizar.urllib.request, "urlopen", fake_urlopen)
    assert atualizar.resolver_versao() == ("v1.2.3", "1.2.3")
    assert capturado["ua"]  # github exige User-Agent


def test_monta_urls_default(monkeypatch):
    monkeypatch.delenv("KOINE_BASE_URL", raising=False)
    zip_url, sha_url = atualizar.montar_urls("v0.4.3", "0.4.3")
    assert zip_url == "https://github.com/jrunic/koine/releases/download/v0.4.3/koine-0.4.3.zip"
    assert sha_url == "https://github.com/jrunic/koine/releases/download/v0.4.3/SHA256SUMS"


def test_monta_urls_espelho(monkeypatch):
    monkeypatch.setenv("KOINE_BASE_URL", "http://espelho.interno/koine")
    zip_url, _ = atualizar.montar_urls("v0.4.3", "0.4.3")
    assert zip_url == "http://espelho.interno/koine/v0.4.3/koine-0.4.3.zip"


def test_verifica_sha256_ok():
    dados = b"conteudo do zip"
    h = hashlib.sha256(dados).hexdigest()
    atualizar.verificar_sha256(dados, f"{h}  koine-0.4.3.zip\n", "koine-0.4.3.zip")


def test_verifica_sha256_divergente():
    with pytest.raises(atualizar.AtualizarErro):
        atualizar.verificar_sha256(b"x", "deadbeef  koine-0.4.3.zip\n", "koine-0.4.3.zip")


import os


def test_substituir_pyz_sucesso(tmp_path):
    src = tmp_path / "novo.pyz"; src.write_bytes(b"novo")
    dst = tmp_path / "dist" / "koine.pyz"; dst.parent.mkdir(); dst.write_bytes(b"velho")
    atualizar._substituir_pyz(str(src), str(dst))
    assert dst.read_bytes() == b"novo" and not src.exists()


def test_substituir_pyz_retenta_em_permissionerror(tmp_path, monkeypatch):
    src = tmp_path / "novo.pyz"; src.write_bytes(b"novo")
    dst = tmp_path / "koine.pyz"; dst.write_bytes(b"velho")
    n = {"c": 0}
    real = os.replace

    def flaky(a, b):
        n["c"] += 1
        if n["c"] < 3:
            raise PermissionError("em uso")
        real(a, b)

    monkeypatch.setattr(atualizar.os, "replace", flaky)
    monkeypatch.setattr(atualizar.time, "sleep", lambda _: None)
    atualizar._substituir_pyz(str(src), str(dst))
    assert dst.read_bytes() == b"novo" and n["c"] == 3


def test_refresh_skills_instala_nos_detectados_com_a_versao_entrante(monkeypatch):
    """A versão que chega ao instalador de skills é a que está ENTRANDO, não a
    do processo em execução: no `atualizar` o pyz ainda é o antigo quando as
    skills são refrescadas, então ler `__version__` lá dentro gravaria o backup
    debaixo da pasta da versão velha."""
    chamados = []
    monkeypatch.setattr(atualizar.skills, "detectar_harnesses", lambda: ["claude", "codex"])
    monkeypatch.setattr(atualizar.skills, "instalar_habilidades_detalhado",
                        lambda h, versao: (chamados.append((h, versao)), (["kn-99"], [], []))[1])
    atualizar._refresh_skills("9.9.9")
    assert chamados == [("claude", "9.9.9"), ("codex", "9.9.9")]
    from koine._version import __version__ as instalada
    assert "9.9.9" != instalada, "a fixture precisa diferir da versão do processo"


from koine._version import __version__


def test_preparar_noop_quando_ja_na_versao(monkeypatch, capsys):
    monkeypatch.setenv("KOINE_VERSAO", f"v{__version__}")
    baixou = {"n": 0}
    monkeypatch.setattr(atualizar, "baixar", lambda url: baixou.__setitem__("n", baixou["n"] + 1))
    assert atualizar.preparar(force=False) == (None, __version__)
    assert baixou["n"] == 0
    assert __version__ in capsys.readouterr().out


def test_mensagem_ja_recente():
    from koine import mensagens
    assert "0.4.3" in mensagens.atualizar_ja_recente("0.4.3")


def test_baixar_fallback_curl_qualquer_plataforma(monkeypatch):
    """SSL falha no urllib; cai pro curl do sistema — em qualquer plataforma
    (macOS Keychain, Windows Schannel, Linux CA bundle)."""
    for plat in ("darwin", "linux", "win32"):
        monkeypatch.setattr(atualizar.sys, "platform", plat)

        def urlopen_falha(req, timeout=60):
            raise atualizar.ssl.SSLError("cert")
        monkeypatch.setattr(atualizar.urllib.request, "urlopen", urlopen_falha)

        class R:
            returncode = 0
            stdout = b"ZIPBYTES"
        monkeypatch.setattr(atualizar.subprocess, "run", lambda *a, **k: R())
        assert atualizar.baixar("https://x/y.zip") == b"ZIPBYTES"


def test_baixar_sem_curl_levanta_com_orientacao(monkeypatch):
    """SSL falha e curl ausente/falha → erro orientativo, em qualquer plataforma."""
    monkeypatch.setattr(atualizar.sys, "platform", "darwin")

    def urlopen_falha(req, timeout=60):
        raise atualizar.ssl.SSLError("cert")
    monkeypatch.setattr(atualizar.urllib.request, "urlopen", urlopen_falha)

    class R:
        returncode = 1
        stdout = b""
    monkeypatch.setattr(atualizar.subprocess, "run", lambda *a, **k: R())
    with pytest.raises(atualizar.AtualizarErro) as ei:
        atualizar.baixar("https://x/y.zip")
    assert "install.sh" in str(ei.value)


def test_resolver_versao_fallback_curl(monkeypatch):
    """resolver_versao: SSL falha no urllib HEAD; curl segue o redirect e
    devolve a tag final (o passo que travava no macOS)."""
    monkeypatch.delenv("KOINE_VERSAO", raising=False)

    def urlopen_falha(req, timeout=30):
        raise atualizar.ssl.SSLError("cert")
    monkeypatch.setattr(atualizar.urllib.request, "urlopen", urlopen_falha)

    class R:
        returncode = 0
        stdout = "https://github.com/jrunic/koine/releases/tag/v1.2.3"
    monkeypatch.setattr(atualizar.subprocess, "run", lambda *a, **k: R())
    assert atualizar.resolver_versao() == ("v1.2.3", "1.2.3")


def test_resolver_versao_sem_curl_levanta(monkeypatch):
    """SSL falha e curl indisponível → erro orientativo com KOINE_VERSAO."""
    monkeypatch.delenv("KOINE_VERSAO", raising=False)

    def urlopen_falha(req, timeout=30):
        raise atualizar.ssl.SSLError("cert")
    monkeypatch.setattr(atualizar.urllib.request, "urlopen", urlopen_falha)

    def sem_curl(*a, **k):
        raise OSError("curl ausente")
    monkeypatch.setattr(atualizar.subprocess, "run", sem_curl)
    with pytest.raises(atualizar.AtualizarErro) as ei:
        atualizar.resolver_versao()
    assert "KOINE_VERSAO" in str(ei.value)


# --- os wrappers saem da lista da versao ENTRANTE (jd-task #749) -------------

def _staging_com_pyz(tmp_path, corpo: str):
    """Staging minimo cujo `koine.pyz` e um script Python de verdade.

    Script e nao zipapp de proposito: o que se mede e que o `atualizar` INVOCA o
    artefato novo, e o interpretador roda `.py` e `.pyz` pela mesma porta.
    """
    staging = tmp_path / "staging"
    (staging / "vault").mkdir(parents=True)
    (staging / "koine.pyz").write_text(corpo, encoding="utf-8")
    return staging


def _aplicar(tmp_path, monkeypatch, corpo):
    monkeypatch.setattr(atualizar._instalar, "extrair", lambda *a, **k: ([], []))
    monkeypatch.setattr(atualizar.skills, "detectar_harnesses", lambda: [])
    staging = _staging_com_pyz(tmp_path, corpo)
    alvo = tmp_path / "koine.pyz"; alvo.write_text("pyz velho", encoding="utf-8")
    bindir = tmp_path / "bin"; bindir.mkdir()
    atualizar.aplicar(str(staging), str(alvo), str(bindir), "9.9.9", force=False)
    return bindir


SENTINELA = '''import sys, os, pathlib
# o "wrapper que so a versao nova conhece"
i = sys.argv.index("--bin")
pathlib.Path(sys.argv[i+1], "kn-do-futuro").write_text("koine.pyz")
'''


def test_wrapper_novo_nasce_no_upgrade(tmp_path, monkeypatch):
    """O defeito: `aplicar` roda no processo do pyz VELHO, entao a lista de
    wrappers e a dele — e wrapper introduzido pela versao nova nunca nasce.
    Silencioso: exit 0 e `koine versao` correta.

    Medido em 01/09/2026 na maquina de um usuario: upgrade 0.5.2 -> 0.10.0 por
    `koine atualizar` deixou a instalacao sem os tres `kn-*-paseo`, e o
    `paseo-info` da versao nova PRESCREVE um nome que nao existe no disco.

    O discriminador e um wrapper que SO o artefato novo sabe criar: se a
    geracao continuar acontecendo no processo antigo, ele nao aparece.
    """
    bindir = _aplicar(tmp_path, monkeypatch, SENTINELA)
    assert (bindir / "kn-do-futuro").exists(), \
        "a lista de wrappers ainda vem do pyz que esta executando"


def test_upgrade_que_nao_consegue_delegar_avisa_e_nao_fica_sem_wrapper(
        tmp_path, monkeypatch, capsys):
    """Se o artefato novo nao souber gerar wrappers — comando renomeado numa
    versao futura —, o `atualizar` volta a gerar pela lista antiga. Isso
    REPRODUZ o defeito, entao nao pode ser silencioso: fallback mudo troca uma
    falha visivel por uma intermitente.
    """
    bindir = _aplicar(tmp_path, monkeypatch, 'import sys; sys.exit(2)')
    assert (bindir / "koine").exists(), "ficou sem wrapper nenhum"
    err = capsys.readouterr().err
    assert "koine instalar" in err, "o fallback precisa dizer como completar"
