---
id: 202607211300
projeto: koine
tipo: plano
status: rascunho
tags: [plano-execucao, koine, atualizar, self-update]
spec: 20260721-koine-atualizar.md
---

# `koine atualizar` — Plano de Implementação

**Objetivo:** Adicionar o subcomando `koine atualizar`, que baixa e aplica a versão mais recente do Koine (pacote + skills) inteiramente em Python, sem tocar `.bat`/`.ps1`/powershell.
**Incremento:** fora do roadmap (spec em caminho curto).
**Arquitetura:** Novo módulo `atualizar.py` resolve versão-alvo (env `KOINE_VERSAO` ou redirect de `releases/latest`), baixa o `.zip` via `urllib`, verifica `SHA256SUMS`, extrai para staging temporário e aplica reusando `instalar.extrair` (com refresh forçado do vault shipped, preservando `dominios` do usuário) + `wrappers.gerar` + refresh de skills. A auto-troca do pyz é in-process no POSIX (`os.replace`) e, no Windows, delegada a um processo-filho da versão nova cujo stdio é redirecionado para log (processo destacado não tem console).
**Pilha técnica:** Python 3.12 stdlib (`urllib.request`, `zipfile`, `hashlib`, `tempfile`, `subprocess`), pytest.

---

## Mapa de Arquivos

- **Criar:** `src/koine/atualizar.py` — resolução de versão, download, verificação, extração e aplicação (troca de pyz + vault + wrappers + skills). Sem shell-out.
- **Modificar:** `src/koine/instalar.py` — `extrair` ganha `atualizar_vault` (força vault shipped, preserva `dominios`).
- **Modificar:** `src/koine/cli.py` — `SUBCOMANDOS` + dispatch + `_cmd_atualizar` (fase-1 POSIX + ramo `--finalizar` do Windows).
- **Modificar:** `src/koine/mensagens.py` — mensagem de já-atualizado.
- **Criar:** `tests/test_atualizar.py` — unit: resolução (env + github), URL, SHA256, retry do `os.replace`, refresh de skills, no-op.
- **Criar:** `tests/test_instalar.py` — unit do `atualizar_vault`.
- **Criar:** `tests/test_atualizar_e2e.py` — e2e com release falsa: no-op; `--force` mesma versão; upgrade real com delta de versão; skill nova refrescada.
- **Modificar (tail):** `src/koine/_version.py`, `pyproject.toml`, `CHANGELOG.md` — bump 0.4.3.

Constante de repo: `REPO = "jrunic/koine"` (topo de `atualizar.py`).

---

## Task 1: Resolução da versão-alvo (env + github)

**Arquivos:** Criar `src/koine/atualizar.py`; Testar `tests/test_atualizar.py`

- [ ] **Step 1: Teste falhante**

```python
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
```

- [ ] **Step 2: Roda e verifica falha**

Comando: `.venv/bin/pytest tests/test_atualizar.py -q`
Esperado: FAIL — `ModuleNotFoundError: No module named 'koine.atualizar'`

- [ ] **Step 3: Implementação**

```python
# src/koine/atualizar.py
import hashlib
import os
import ssl
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

from koine import instalar as _instalar, mensagens, skills, wrappers
from koine._version import __version__

REPO = "jrunic/koine"


class AtualizarErro(Exception):
    """Falha de rede/resolução/verificação, com mensagem pronta ao usuário."""


def resolver_versao() -> tuple[str, str]:
    """(tag, versao). KOINE_VERSAO fixa a tag; senão segue o redirect de
    releases/latest no github. Não baixa o pacote."""
    pin = os.environ.get("KOINE_VERSAO")
    if pin:
        tag = pin if pin.startswith("v") else f"v{pin}"
        return tag, tag[1:]
    url = f"https://github.com/{REPO}/releases/latest"
    try:
        req = urllib.request.Request(
            url, method="HEAD", headers={"User-Agent": "koine-atualizar"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            final = resp.geturl()
    except (urllib.error.URLError, ssl.SSLError, OSError) as e:
        raise AtualizarErro(
            f"não foi possível resolver a última versão pelo github ({e}). "
            "Fixe a versão: KOINE_VERSAO=vX.Y.Z koine atualizar") from e
    tag = final.rstrip("/").rsplit("/", 1)[-1]
    if not tag.startswith("v"):
        raise AtualizarErro(
            f"resposta inesperada de releases/latest: {final!r}. "
            "Fixe a versão: KOINE_VERSAO=vX.Y.Z koine atualizar")
    return tag, tag[1:]
```

- [ ] **Step 4: Roda e verifica passa**

Comando: `.venv/bin/pytest tests/test_atualizar.py -q`
Esperado: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/koine/atualizar.py tests/test_atualizar.py
git commit -m "feat(atualizar): resolução da versão-alvo (KOINE_VERSAO ou releases/latest com User-Agent)"
```

---

## Task 2: URLs + download + verificação SHA256

**Arquivos:** Modificar `src/koine/atualizar.py`; Testar `tests/test_atualizar.py`

- [ ] **Step 1: Teste falhante**

```python
# tests/test_atualizar.py (append)
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
```

- [ ] **Step 2: Roda e verifica falha**

Comando: `.venv/bin/pytest tests/test_atualizar.py -k "urls or sha" -q`
Esperado: FAIL — `AttributeError: module 'koine.atualizar' has no attribute 'montar_urls'`

- [ ] **Step 3: Implementação**

```python
# src/koine/atualizar.py (append)
def montar_urls(tag: str, versao: str) -> tuple[str, str]:
    base = (os.environ.get("KOINE_BASE_URL")
            or f"https://github.com/{REPO}/releases/download").rstrip("/")
    return f"{base}/{tag}/koine-{versao}.zip", f"{base}/{tag}/SHA256SUMS"


def baixar(url: str) -> bytes:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "koine-atualizar"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except (urllib.error.URLError, ssl.SSLError, OSError) as e:
        raise AtualizarErro(
            f"falha ao baixar {url} ({e}). Verifique a conexão ou o KOINE_BASE_URL; "
            "a instalação atual não foi tocada.") from e


def baixar_sums_opcional(sha_url: str) -> str | None:
    try:
        req = urllib.request.Request(sha_url, headers={"User-Agent": "koine-atualizar"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, ssl.SSLError, OSError):
        return None


def verificar_sha256(dados: bytes, sums_texto: str, asset: str) -> None:
    esperado = None
    for linha in sums_texto.splitlines():
        partes = linha.split()
        if len(partes) == 2 and partes[1].lstrip("*") == asset:
            esperado = partes[0].lower()
            break
    if esperado is None:
        raise AtualizarErro(f"{asset} ausente no SHA256SUMS")
    real = hashlib.sha256(dados).hexdigest()
    if real != esperado:
        raise AtualizarErro(
            f"hash divergente para {asset}: esperado {esperado}, obtido {real}. "
            "Download corrompido; instalação atual intacta.")
```

- [ ] **Step 4: Roda e verifica passa**

Comando: `.venv/bin/pytest tests/test_atualizar.py -k "urls or sha" -q`
Esperado: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/koine/atualizar.py tests/test_atualizar.py
git commit -m "feat(atualizar): URLs (KOINE_BASE_URL), download e verificação SHA256"
```

---

## Task 3: Troca segura do pyz com retry (`_substituir_pyz`)

**Arquivos:** Modificar `src/koine/atualizar.py`; Testar `tests/test_atualizar.py`

- [ ] **Step 1: Teste falhante**

```python
# tests/test_atualizar.py (append)
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
```

- [ ] **Step 2: Roda e verifica falha**

Comando: `.venv/bin/pytest tests/test_atualizar.py -k substituir -q`
Esperado: FAIL — `AttributeError: ... has no attribute '_substituir_pyz'`

- [ ] **Step 3: Implementação**

```python
# src/koine/atualizar.py (append)
def _substituir_pyz(src: str, dst: str, tentativas: int = 50, intervalo: float = 0.2) -> None:
    """os.replace atômico do pyz. No Windows o processo pai pode ainda segurar o
    dst; reitera até liberar. No POSIX acerta de primeira. Sem trampolim batch."""
    for i in range(tentativas):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if i == tentativas - 1:
                raise
            time.sleep(intervalo)
```

- [ ] **Step 4: Roda e verifica passa**

Comando: `.venv/bin/pytest tests/test_atualizar.py -k substituir -q`
Esperado: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add src/koine/atualizar.py tests/test_atualizar.py
git commit -m "feat(atualizar): troca atômica do pyz com retry (Windows-safe, sem batch)"
```

---

## Task 4: `extrair` refresca vault shipped e preserva `dominios` do usuário

Motivo (verificado em `instalar.extrair`): só `dominios/` roteia para `config_dir` (do usuário); o resto vai para `vault_dir` (shipped). `_copiar` com `force=False` **pula** arquivos alterados. Num upgrade isso deixa o vault velho; `force=True` global **clobbera** os `dominios` do usuário. Solução: flag `atualizar_vault` que força só o vault, mantendo `dominios` sob a regra de divergência.

**Arquivos:** Modificar `src/koine/instalar.py`; Testar `tests/test_instalar.py`

- [ ] **Step 1: Teste falhante**

```python
# tests/test_instalar.py
import os
from koine import instalar, paths


def test_atualizar_vault_forca_vault_preserva_dominios(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    for k in ("XDG_DATA_HOME", "XDG_CONFIG_HOME"):
        monkeypatch.delenv(k, raising=False)
    src = tmp_path / "src"
    (src / "conceitos").mkdir(parents=True)
    (src / "dominios").mkdir()
    (src / "KOINE.md").write_text("v1")
    (src / "dominios" / "tecnologia.md").write_text("dom v1")
    instalar.extrair(str(src), "0.0.1")
    dom = os.path.join(paths.config_dir(), "dominios", "tecnologia.md")
    open(dom, "w").write("edicao do usuario")
    (src / "KOINE.md").write_text("v2")
    div = instalar.extrair(str(src), "0.0.2", force=False, atualizar_vault=True)
    assert open(os.path.join(paths.vault_dir(), "KOINE.md")).read() == "v2"
    assert open(dom).read() == "edicao do usuario"
    assert any("dominios" in d for d in div)
```

- [ ] **Step 2: Roda e verifica falha**

Comando: `.venv/bin/pytest tests/test_instalar.py -q`
Esperado: FAIL — `TypeError: extrair() got an unexpected keyword argument 'atualizar_vault'`

- [ ] **Step 3: Implementação**

Muda a assinatura de `extrair`:

```python
def extrair(vault_src: str, versao: str, force: bool = False,
            atualizar_vault: bool = False) -> list[str]:
```

E o roteamento por arquivo (substitui o `if/else` que definia `dest` + a chamada única `_copiar`):

```python
            if rel.startswith("dominios/"):
                dest = os.path.join(config_dir, rel.replace("/", os.sep))
                _copiar(src, dest, force, divergencias)                     # usuário: preserva
            else:
                dest = os.path.join(vault_dir, rel.replace("/", os.sep))
                _copiar(src, dest, force or atualizar_vault, divergencias)  # shipped: refresca
```

- [ ] **Step 4: Roda e verifica passa**

Comando: `.venv/bin/pytest tests/test_instalar.py -q`
Esperado: PASS (1 passed)

- [ ] **Step 5: Regressão do instalar (default inalterado)**

Comando: `.venv/bin/pytest tests/test_installer_e2e.py tests/test_pyz_e2e.py -q`
Esperado: PASS — `atualizar_vault=False` por default preserva o comportamento do `koine instalar`.

- [ ] **Step 6: Commit**

```bash
git add src/koine/instalar.py tests/test_instalar.py
git commit -m "feat(instalar): extrair(atualizar_vault) força vault shipped preservando dominios"
```

---

## Task 5: Aplicação (extrai vault, troca pyz, wrappers, skills)

**Arquivos:** Modificar `src/koine/atualizar.py`; Testar `tests/test_atualizar.py`

- [ ] **Step 1: Teste falhante (refresh de skills)**

```python
# tests/test_atualizar.py (append)
def test_refresh_skills_instala_nos_detectados(monkeypatch):
    chamados = []
    monkeypatch.setattr(atualizar.skills, "detectar_harnesses", lambda: ["claude", "codex"])
    monkeypatch.setattr(atualizar.skills, "instalar_habilidades_detalhado",
                        lambda h, force=False: (chamados.append((h, force)), (["kn-99"], [], []))[1])
    atualizar._refresh_skills(force=True)
    assert chamados == [("claude", True), ("codex", True)]
```

- [ ] **Step 2: Roda e verifica falha**

Comando: `.venv/bin/pytest tests/test_atualizar.py -k refresh -q`
Esperado: FAIL — `AttributeError: ... has no attribute '_refresh_skills'`

- [ ] **Step 3: Implementação**

```python
# src/koine/atualizar.py (append)
def _refresh_skills(force: bool = False) -> None:
    """Instala/atualiza skills do vault novo em cada harness detectado.
    Idempotente; divergentes preservados salvo force. Falha por harness não aborta."""
    for h in skills.detectar_harnesses():
        try:
            criadas, _exist, div = skills.instalar_habilidades_detalhado(h, force=force)
            for n in criadas:
                print(f"    + {h}: {n}")
            if div:
                print(f"    ! {h}: divergentes preservadas (use --force): {', '.join(div)}")
        except (OSError, ValueError) as e:
            print(f"    aviso: skills de {h}: {e}", file=sys.stderr)


def aplicar(staging: str, alvo_pyz: str, bindir: str, versao: str, force: bool) -> None:
    """Fase de aplicação (não-transacional; recuperável re-rodando). Extrai o
    vault (shipped forçado, dominios do usuário preservados salvo force), troca o
    pyz, regenera wrappers baqueando o interpretador atual e refresca skills."""
    _instalar.extrair(os.path.join(staging, "vault"), versao,
                      force=force, atualizar_vault=True)
    _substituir_pyz(os.path.join(staging, "koine.pyz"), alvo_pyz)
    wrappers.gerar(bindir, alvo_pyz, sys.executable)
    print("Skills:")
    _refresh_skills(force=force)
    print(f"Koine atualizado para {versao}.")
```

- [ ] **Step 4: Roda e verifica passa**

Comando: `.venv/bin/pytest tests/test_atualizar.py -k refresh -q`
Esperado: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add src/koine/atualizar.py tests/test_atualizar.py
git commit -m "feat(atualizar): aplicação (vault forçado + pyz + wrappers + refresh de skills)"
```

---

## Task 6: Orquestração fase-1 (`preparar`) + no-op

**Arquivos:** Modificar `src/koine/atualizar.py`; Testar `tests/test_atualizar.py`

- [ ] **Step 1: Teste falhante**

```python
# tests/test_atualizar.py (append)
from koine._version import __version__


def test_preparar_noop_quando_ja_na_versao(monkeypatch, capsys):
    monkeypatch.setenv("KOINE_VERSAO", f"v{__version__}")
    baixou = {"n": 0}
    monkeypatch.setattr(atualizar, "baixar", lambda url: baixou.__setitem__("n", baixou["n"] + 1))
    assert atualizar.preparar(force=False) == (None, __version__)
    assert baixou["n"] == 0
    assert __version__ in capsys.readouterr().out
```

- [ ] **Step 2: Roda e verifica falha**

Comando: `.venv/bin/pytest tests/test_atualizar.py -k preparar -q`
Esperado: FAIL — `AttributeError: ... has no attribute 'preparar'`

- [ ] **Step 3: Implementação**

```python
# src/koine/atualizar.py (append)
def preparar(force: bool = False) -> tuple[str | None, str]:
    """Resolve versão; no-op (sem baixar) se já estamos nela; senão baixa +
    verifica + extrai para staging. Devolve (staging, versao) — staging=None no
    no-op. `versao` sempre volta (evita re-derivar do pyz)."""
    tag, versao = resolver_versao()
    if versao == __version__ and not force:
        print(mensagens.atualizar_ja_recente(versao))
        return None, versao
    zip_url, sha_url = montar_urls(tag, versao)
    asset = f"koine-{versao}.zip"
    dados = baixar(zip_url)
    sums = baixar_sums_opcional(sha_url)
    if sums is not None:
        verificar_sha256(dados, sums, asset)
    else:
        print(f"aviso: {asset} sem SHA256SUMS na origem — seguindo sem verificação.")
    staging = tempfile.mkdtemp(prefix="koine-upd-")
    zip_path = os.path.join(staging, asset)
    with open(zip_path, "wb") as f:
        f.write(dados)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(staging)
    os.remove(zip_path)
    return staging, versao
```

- [ ] **Step 4: Roda e verifica passa**

Comando: `.venv/bin/pytest tests/test_atualizar.py -k preparar -q`
Esperado: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add src/koine/atualizar.py tests/test_atualizar.py
git commit -m "feat(atualizar): preparar() -> (staging, versao) com no-op sem download"
```

---

## Task 7: Wiring do subcomando no `cli.py`

**Arquivos:** Modificar `src/koine/cli.py`; Testar `tests/test_cli_e2e.py`

- [ ] **Step 1: Teste falhante**

```python
# tests/test_cli_e2e.py (append)
def test_atualizar_falha_rede_retorna_1(monkeypatch):
    from koine import cli, atualizar
    def boom(force=False):
        raise atualizar.AtualizarErro("sem rede")
    monkeypatch.setattr(atualizar, "preparar", boom)
    assert cli.main(["atualizar"]) == 1
```

- [ ] **Step 2: Roda e verifica falha**

Comando: `.venv/bin/pytest tests/test_cli_e2e.py -k atualizar -q`
Esperado: FAIL — retorna 2 (desconhecido), não 1

- [ ] **Step 3: Implementação**

Linha 25 — adiciona `"atualizar"`:

```python
SUBCOMANDOS = {"versao", "instalar", "instalar-habilidades", "gerar", "mostrar", "atualizar"}
```

Import de `koine` (linhas 7-22) — inclui `atualizar as _atualizar,`.

Dispatch em `main` (após o bloco `mostrar`):

```python
        if primeiro == "atualizar":
            return _cmd_atualizar(argv[1:])
```

Handler novo (após `_cmd_mostrar`):

```python
def _cmd_atualizar(args: list[str]) -> int:
    p = argparse.ArgumentParser(prog="koine atualizar")
    p.add_argument("--force", action="store_true")
    # ramo interno de finalização no Windows (pai destacado já saiu):
    p.add_argument("--finalizar", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--staging", default=None, help=argparse.SUPPRESS)
    p.add_argument("--alvo-pyz", dest="alvo_pyz", default=None, help=argparse.SUPPRESS)
    p.add_argument("--bin", default=None, help=argparse.SUPPRESS)
    p.add_argument("--versao", default=None, help=argparse.SUPPRESS)
    ns = p.parse_args(args)

    alvo_pyz = ns.alvo_pyz or _pyz_padrao()
    bindir = ns.bin or _bin_padrao()

    # Fase 2 (Windows): roda do pyz staged; aplica após o pai liberar o alvo.
    if ns.finalizar:
        _atualizar.aplicar(ns.staging, alvo_pyz, bindir, ns.versao, force=ns.force)
        return 0

    # Fase 1: resolve + baixa para staging (no-op sai aqui).
    try:
        staging, versao = _atualizar.preparar(force=ns.force)
    except _atualizar.AtualizarErro as e:
        print(str(e), file=sys.stderr)
        return 1
    if staging is None:
        return 0

    if sys.platform == "win32":
        # Pai segura o alvo_pyz; delega ao filho DESTACADO (sem console → stdio
        # para log, senão print() do filho lança WinError 6 e a troca morre muda).
        import subprocess
        staged_pyz = os.path.join(staging, "koine.pyz")
        logpath = os.path.join(paths.cache_dir(), "atualizar.log")
        os.makedirs(os.path.dirname(logpath), exist_ok=True)
        logf = open(logpath, "w", encoding="utf-8")
        DETACHED = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        subprocess.Popen(
            [sys.executable, staged_pyz, "atualizar", "--finalizar",
             "--staging", staging, "--alvo-pyz", alvo_pyz, "--bin", bindir,
             "--versao", versao] + (["--force"] if ns.force else []),
            stdout=logf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            creationflags=DETACHED, close_fds=True)
        print(f"Baixado {versao}. Aplicando em segundo plano — confirme com "
              f"`koine versao` em alguns segundos (log: {logpath}).")
        return 0

    # POSIX: sem lock, aplica in-process.
    _atualizar.aplicar(staging, alvo_pyz, bindir, versao, force=ns.force)
    return 0
```

- [ ] **Step 4: Roda e verifica passa**

Comando: `.venv/bin/pytest tests/test_cli_e2e.py -k atualizar -q`
Esperado: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add src/koine/cli.py tests/test_cli_e2e.py
git commit -m "feat(atualizar): subcomando koine atualizar (POSIX in-process + handoff Windows com log)"
```

---

## Task 8: Mensagem amigável

**Arquivos:** Modificar `src/koine/mensagens.py`; Testar `tests/test_atualizar.py`

- [ ] **Step 1: Teste falhante**

```python
# tests/test_atualizar.py (append)
from koine import mensagens


def test_mensagem_ja_recente():
    assert "0.4.3" in mensagens.atualizar_ja_recente("0.4.3")
```

- [ ] **Step 2: Roda e verifica falha**

Comando: `.venv/bin/pytest tests/test_atualizar.py -k mensagem -q`
Esperado: FAIL — `AttributeError: module 'koine.mensagens' has no attribute 'atualizar_ja_recente'`

- [ ] **Step 3: Implementação**

```python
# src/koine/mensagens.py (append)
def atualizar_ja_recente(versao: str) -> str:
    return f"Koine já está na versão {versao}."
```

(A `preparar` da Task 6 já a usa — nada mais a ligar.)

- [ ] **Step 4: Roda e verifica passa**

Comando: `.venv/bin/pytest tests/test_atualizar.py -k mensagem -q`
Esperado: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add src/koine/mensagens.py tests/test_atualizar.py
git commit -m "feat(atualizar): mensagem de já-atualizado"
```

---

## Task 9: e2e contra release falsa (no-op, --force, upgrade com delta, skill nova)

**Arquivos:** Criar `tests/test_atualizar_e2e.py`

- [ ] **Step 1: Teste**

```python
# tests/test_atualizar_e2e.py
import http.server
import os
import re
import shutil
import socketserver
import subprocess
import sys
import threading
from functools import partial

import pytest

from koine._version import __version__

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _servir(www: str):
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=www)
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _build_zip(destino_out: str, src_repo: str = REPO):
    subprocess.run([sys.executable, os.path.join(src_repo, "scripts", "build-pyz.py"),
                    "--out", destino_out, "--zip"], check=True, capture_output=True, text=True)


def _repo_com_versao(tmp_path, nova_versao: str) -> str:
    """Copia o repo para tmp e reescreve _version — para gerar um zip de versão
    diferente e exercitar o upgrade real (User Story #1)."""
    dst = str(tmp_path / f"repo-{nova_versao}")
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns(
        ".git", ".venv", "dist", "__pycache__"))
    vf = os.path.join(dst, "src", "koine", "_version.py")
    open(vf, "w").write(f'__version__ = "{nova_versao}"\n')
    return dst


@pytest.mark.skipif(sys.platform == "win32", reason="fase-1 in-process é POSIX; Windows tem handoff próprio")
def test_atualizar_noop_e_upgrade_real(tmp_path):
    # skill nova para provar refresh
    skill = os.path.join(REPO, "vault", "habilidades", "kn-99-teste")
    os.makedirs(skill, exist_ok=True)
    open(os.path.join(skill, "SKILL.md"), "w").write("# kn-99-teste\n")
    try:
        # base = versão atual instalada
        base_out = str(tmp_path / "base")
        _build_zip(base_out)
        # alvo = versão maior
        nova = "9.9.9"
        alvo_out = str(tmp_path / "alvo")
        _build_zip(alvo_out, _repo_com_versao(tmp_path, nova))

        # serve a release ALVO
        www = tmp_path / "www" / f"v{nova}"; www.mkdir(parents=True)
        shutil.copy(os.path.join(alvo_out, f"koine-{nova}.zip"), str(www))
        srv = _servir(str(tmp_path / "www"))

        home = tmp_path / "home"; home.mkdir()
        fakebin = tmp_path / "fakebin"; fakebin.mkdir()
        claude = fakebin / "claude"; claude.write_text("#!/bin/sh\n"); claude.chmod(0o755)
        path = os.path.dirname(sys.executable) + os.pathsep + str(fakebin) + os.pathsep + "/usr/bin:/bin"
        env = {"HOME": str(home), "PATH": path,
               "KOINE_BASE_URL": f"http://127.0.0.1:{srv.server_address[1]}"}

        # instala a BASE
        dist = home / ".local/share/koine/dist"; dist.mkdir(parents=True)
        subprocess.run([sys.executable, "-m", "zipfile", "-e",
                        os.path.join(base_out, f"koine-{__version__}.zip"), str(dist)], check=True)
        pyz = str(dist / "koine.pyz")
        subprocess.run([sys.executable, pyz, "instalar"], env=env,
                       stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True)

        # 1) no-op: pin na versão instalada, sem --force
        r = subprocess.run([sys.executable, pyz, "atualizar"],
                           env={**env, "KOINE_VERSAO": f"v{__version__}"},
                           capture_output=True, text=True)
        assert r.returncode == 0 and "já está na versão" in r.stdout

        # 2) upgrade real SEM --force: pin na versão maior (User Story #1)
        r = subprocess.run([sys.executable, pyz, "atualizar"],
                           env={**env, "KOINE_VERSAO": f"v{nova}"},
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr + r.stdout
        # pyz trocado → koine versao reporta a nova
        v = subprocess.run([sys.executable, pyz, "versao"], env=env,
                           capture_output=True, text=True).stdout
        assert nova in v
        # skill nova refrescada no harness detectado
        assert os.path.isdir(os.path.join(str(home), ".claude/skills/kn-99-teste"))
    finally:
        srv.shutdown(); srv.server_close()
        shutil.rmtree(skill, ignore_errors=True)
```

- [ ] **Step 2: Roda e verifica**

Comando: `.venv/bin/pytest tests/test_atualizar_e2e.py -q`
Esperado: PASS (1 passed). Falha aqui aponta a task de origem (preparar/aplicar/extrair) — corrigir antes de seguir.

- [ ] **Step 3: Confirma vault limpo**

Comando: `git status --short vault/`
Esperado: (vazio) — o `finally` removeu `kn-99-teste`.

- [ ] **Step 4: Commit**

```bash
git add tests/test_atualizar_e2e.py
git commit -m "test(atualizar): e2e — no-op, upgrade real com delta de versão, skill nova refrescada"
```

---

## Task 10: Suíte completa + bump 0.4.3 + CHANGELOG

**Arquivos:** Modificar `src/koine/_version.py`, `pyproject.toml`, `CHANGELOG.md`

- [ ] **Step 1: Suíte completa verde**

Comando: `.venv/bin/pytest -q`
Esperado: todos passam (120 baseline + novos).

- [ ] **Step 2: Bump (fonte única)**

`src/koine/_version.py`: `__version__ = "0.4.3"` · `pyproject.toml`: `version = "0.4.3"`

- [ ] **Step 3: CHANGELOG — Unreleased → 0.4.3**

Renomeia `## [Unreleased]` para `## [0.4.3] — 2026-07-21` (mantendo as entradas Fixed/Changed do fix de agente já lá) e adiciona:

```markdown
### Added

- **Comando `koine atualizar`** — self-update para a última release (ou versão fixada em `KOINE_VERSAO`), baixando o `.zip` do github (ou de `KOINE_BASE_URL`), verificando `SHA256SUMS`, e reaproveitando o caminho de instalação: refresca o vault shipped preservando os `dominios` do usuário, regenera os wrappers e reinstala skills nos harnesses detectados. Execução 100% Python — nenhum `.bat`/`.ps1`/powershell — para políticas que bloqueiam executáveis e powershell (ex.: Grupo Aldo). Auto-troca do pyz é in-process no POSIX e delegada a um processo-filho da versão nova no Windows (stdio em log, sem trampolim batch). No-op quando já na versão-alvo; `--force` reinstala.
```

Adiciona `## [Unreleased]` vazio acima de `## [0.4.3]`.

- [ ] **Step 4: Gate de versão única**

Comando: `.venv/bin/pytest tests/test_versao.py -q`
Esperado: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/koine/_version.py pyproject.toml CHANGELOG.md
git commit -m "chore: bump para v0.4.3 (koine atualizar + fix de resolução de agente)"
```

---

## Auto-Revisão

### 1. Cobertura da Spec

| Requisito | Task |
|---|---|
| Subcomando `atualizar` | 7 |
| Resolução de versão (env + latest github) | 1 |
| No-op sem download | 6 |
| Download `.zip` stdlib (nunca `.exe`) | 2, 6 |
| KOINE_BASE_URL (espelho) | 2 |
| SHA256 (degrada se ausente) | 2, 6 |
| Auto-troca sem batch (POSIX in-process / Windows filho com log) | 3, 7 |
| Falha de rede sem tocar instalação (erro antes de qualquer escrita em dist) | 1, 2, 7 |
| Vault shipped refrescado, `dominios` do usuário preservados | 4, 5 |
| Refresh de skills nos detectados (idempotente, preserva divergentes) | 5 |
| Execução 100% Python (único subprocess = `sys.executable`) | 3, 5, 7 |
| Downgrade via KOINE_VERSAO (compara igualdade, não "só avança") | 1, 6 |
| Bump 0.4.3 + CHANGELOG | 10 |

Sem gaps.

### 2. Placeholders

Nenhum "TBD/TODO/depois". `preparar` devolve `(staging, versao)` direto — sem `_versao_do_pyz` nem linha ilustrativa.

### 3. Consistência de nomes

`resolver_versao`, `montar_urls`, `baixar`, `baixar_sums_opcional`, `verificar_sha256`, `_substituir_pyz`, `_refresh_skills`, `aplicar`, `preparar` (retorna tupla), `AtualizarErro`, `_cmd_atualizar`, `extrair(..., atualizar_vault=)` — idênticos em todas as tasks. `alvo_pyz`/`bindir`/`staging`/`versao` fluem consistentes entre fase-1 e `--finalizar`.

## Limitações de cobertura (honestidade)

- O e2e (Task 9) roda o caminho **POSIX in-process**, incluindo **upgrade real com delta de versão sem `--force`** (User Story #1) e refresh de skill. O ramo **Windows** (`--finalizar` + Popen destacado + retry do `os.replace` + stdio-em-log) **não** roda em CI macOS/Linux; a lógica de retry é unit (Task 3) e `aplicar` é a mesma função dos dois ramos. **Validação real no Windows fica para a VM AppLocker antes do release** — é a fronteira do Aldo e não pode ir a produção sem esse teste manual.
- A resolução `latest` via github é unit com `urlopen` mockado (Task 1); o acerto do redirect real do github (e a exigência de User-Agent) só se confirma contra a rede real — checar num smoke manual antes do release.
