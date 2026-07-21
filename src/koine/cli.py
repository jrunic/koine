import argparse
import os
import pathlib
import shutil
import sys

from koine import (
    adapters,
    atualizar as _atualizar,
    canonica,
    conflito,
    contexto,
    frontmatter,
    indice,
    instalar as _instalar,
    launch,
    mensagens,
    pasta as pasta_mod,
    paths,
    schema,
    skills,
    wrappers,
)
from koine._version import __version__

SUBCOMANDOS = {"versao", "instalar", "instalar-habilidades", "gerar", "mostrar", "atualizar"}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("uso: koine <cliente|subcomando> ...", file=sys.stderr)
        return 2

    primeiro = argv[0]
    if primeiro in SUBCOMANDOS:
        if primeiro == "versao":
            print(f"koine {__version__}")
            return 0
        if primeiro == "instalar":
            return _cmd_instalar(argv[1:])
        if primeiro == "instalar-habilidades":
            return _cmd_instalar_habilidades(argv[1:])
        if primeiro == "gerar":
            return _cmd_gerar(argv[1:])
        if primeiro == "mostrar":
            return _cmd_mostrar(argv[1:])
        if primeiro == "atualizar":
            return _cmd_atualizar(argv[1:])
    if primeiro in adapters.REGISTRY:
        return _rodar_cliente(primeiro, argv[1:])

    print(f"desconhecido: {primeiro}", file=sys.stderr)
    return 2


def _cmd_instalar(args: list[str]) -> int:
    p = argparse.ArgumentParser(prog="koine instalar")
    p.add_argument("--vault", default=None)
    p.add_argument("--bin", default=None)
    p.add_argument("--pyz", default=None)
    p.add_argument("--force", action="store_true")
    p.add_argument("--para", default=None)
    ns = p.parse_args(args)

    vault_src = ns.vault or _localizar_vault()
    div = _instalar.extrair(vault_src, __version__, force=ns.force)
    if div and not ns.force:
        print("Arquivos divergentes (use --force):")
        for d in div:
            print("  !", d)
    bindir = ns.bin or _bin_padrao()
    pyz = ns.pyz or _pyz_padrao()
    # sys.executable = interpretador que rodou `instalar` (>=3.10 garantido);
    # bakear absoluto no wrapper evita `python3` puro pegar um Python antigo.
    wrappers.gerar(bindir, pyz, sys.executable)
    # espelha term.IsTerminal(stdin) do Go (instalar.go:61)
    interativo = sys.stdin.isatty()
    canonica.configurar(vault_src, interativo=interativo)
    try:
        _instalar_com_deteccao(ns.para, interativo, ns.force)
    except (OSError, ValueError) as e:
        # degradação graciosa, instalar.go:68-70 — skills falhando não aborta
        print(f"aviso: skills: {e}", file=sys.stderr)
    print("Instalação concluída.")
    # mensagem final SEMPRE imprime, mesmo com skills falhando (instalar.go:72-83)
    print(mensagens.final_instalar(), end="")
    return 0


def _instalar_com_deteccao(para: str | None, interativo: bool, force: bool = False) -> None:
    """Porta de instalarComDeteccao (instalar.go:91-124): detecta harnesses no
    PATH e instala skills com confirmação. `para` dado → instala sem prompt;
    não-interativo → apenas informa."""
    print("\nInstalando skills de harness:")
    if para:
        _instalar_skills_e_imprimir(para, force)
        return
    detectados = skills.detectar_harnesses()
    if not detectados:
        print(mensagens.orientativa_sem_harness(), end="")
        return
    if not interativo:
        print("  Detectados:", ", ".join(detectados))
        print("  → Modo não-interativo. Para instalar skills: koine instalar-habilidades --para=<harness>")
        return
    for h in detectados:
        print(f"  {h} detectado → instalar skills kn-*? [S/n]: ", end="", flush=True)
        resp = sys.stdin.readline().strip().lower()
        if resp in ("", "s"):
            try:
                _instalar_skills_e_imprimir(h, force)
            except (OSError, ValueError) as e:
                print(f"  aviso: {e}", file=sys.stderr)  # instalar.go:116-118
        else:
            print(f"  → Pulado. Para instalar depois: koine instalar-habilidades --para={h}")


def _instalar_skills_e_imprimir(h: str, force: bool = False) -> None:
    # espelha instalarEImprimir (instalar_habilidades.go:150-167)
    criadas, existentes, div = skills.instalar_habilidades_detalhado(h, force=force)
    home = str(pathlib.Path.home())
    print(f"  Skills para {h} ({os.path.join(home, *skills.HARNESS_SKILLS[h].split('/'))}):")
    for n in criadas:
        print(f"    + {n}")
    for n in existentes:
        print(f"    = {n}")
    if not criadas and not existentes:
        print("    (nenhuma skill kn-* encontrada em vault)")
    if div:
        print("  Skills divergentes preservadas (use --force para sobrescrever):")
        for d in div:
            print("   !", d)


def _cmd_instalar_habilidades(args: list[str]) -> int:
    p = argparse.ArgumentParser(prog="koine instalar-habilidades")
    p.add_argument("--para", required=True)
    p.add_argument("--force", action="store_true")
    ns = p.parse_args(args)
    div = skills.instalar_habilidades(ns.para, force=ns.force)
    if div and not ns.force:
        print("Skills divergentes preservadas (use --force para sobrescrever):")
        for d in div:
            print("  !", d)
    else:
        print(f"Skills instaladas para {ns.para}.")
    return 0


def _localizar_vault() -> str:
    # 1. ao lado do argv0/pyz (payload de distribuição)
    base = os.path.dirname(os.path.abspath(sys.argv[0]))
    for cand in (os.path.join(base, "vault"), os.path.join(base, ".koine-bootstrap")):
        if os.path.isdir(cand):
            return cand
    # 2. dev: repo vault/ relativo a este arquivo (src/koine/cli.py → ../../vault)
    repo_vault = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "vault"))
    if os.path.isdir(repo_vault):
        return repo_vault
    raise SystemExit("vault não encontrado; use --vault <path>")


def _bin_padrao() -> str:
    return os.path.join(str(pathlib.Path.home()), ".local", "bin")


def _pyz_padrao() -> str:
    return os.path.abspath(sys.argv[0])


def _montar_cm(agente: str, pasta: str) -> contexto.ContextoMontado:
    ctx_path = os.path.join(pasta, "CONTEXTO.md")
    fm, _ = frontmatter.ler(open(ctx_path, encoding="utf-8").read())
    # bootstrap não tem escopo nem índices; contexto.resolver trata o ramo.
    if not fm.get("bootstrap"):
        # índices antes do render (o adapter os referencia)
        escopo_fm, _ = frontmatter.ler(
            open(os.path.join(paths.config_dir(), "escopos", f"{fm['escopo']}.md"),
                 encoding="utf-8").read())
        refs = paths.resolver_tagged(schema.Escopo.from_fm(escopo_fm).pasta_referencias)
        indice.gerar(refs, fm.get("dominios", []))
    cm = contexto.resolver(agente, pasta)
    cm.pasta_abs = pasta
    return cm


def _materializar(lanc, pasta: str) -> None:
    """Materializa um Lancamento: working dir → externos → symlinks."""
    for rel, conteudo in lanc.arquivos_working_dir.items():
        p = os.path.join(pasta, rel)
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        conflito.resolver_arquivo_conflito(p)  # symlink/diretório → ConflitoErro
        with open(p, "w", encoding="utf-8") as f:
            f.write(conteudo)
    for absp, conteudo in lanc.arquivos_externos.items():
        os.makedirs(os.path.dirname(absp), exist_ok=True)
        with open(absp, "w", encoding="utf-8") as f:
            f.write(conteudo)
    for link, alvo in lanc.symlinks.items():
        os.makedirs(os.path.dirname(link), exist_ok=True)
        conflito.resolver_symlink_conflito(link, alvo)  # no-op/backup/ConflitoErro
        if os.path.islink(link):
            os.remove(link)  # só chega aqui se alvo correto (no-op) — recriar é idempotente
        _criar_symlink(link, alvo)


def _criar_symlink(link: str, alvo: str) -> None:
    try:
        os.symlink(alvo, link)
    except OSError:
        if sys.platform != "win32":
            raise
        shutil.copyfile(alvo, link)  # Windows sem Developer Mode: cópia regenerada por sessão


def _cmd_gerar(args: list[str]) -> int:
    agente = args[0]
    try:
        pasta = pasta_mod.resolver(args[1] if len(args) >= 2 else "")
    except pasta_mod.ResolucaoErro as e:
        print(str(e), file=sys.stderr)
        return 1
    try:
        cm = _montar_cm(agente, pasta)
    except contexto.AgenteNaoEncontrado as e:
        print(mensagens.agente_nao_encontrado(e.agente, e.disponiveis), file=sys.stderr)
        return 1
    lanc = adapters.get("claude").renderizar(cm)
    conteudo = lanc.arquivos_working_dir["CLAUDE.md"]
    destino = os.path.join(pasta, "CLAUDE.md")
    with open(destino, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"Escrito {destino} ({len(conteudo.encode('utf-8'))} bytes)")
    return 0


def _cmd_mostrar(args: list[str]) -> int:
    agente, alvo = args[0], args[1]
    # alvo NÃO resolve alias — comportamento congelado de `mostrar` (arg cru)
    try:
        cm = _montar_cm(agente, alvo)
    except contexto.AgenteNaoEncontrado as e:
        print(mensagens.agente_nao_encontrado(e.agente, e.disponiveis), file=sys.stderr)
        return 1
    lanc = adapters.get("claude").renderizar(cm)
    print(lanc.arquivos_working_dir["CLAUDE.md"], end="")
    return 0


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


def _rodar_cliente(cliente: str, args: list[str]) -> int:
    agente = args[0]
    try:
        pasta = pasta_mod.resolver(args[1] if len(args) >= 2 else "")
    except pasta_mod.ResolucaoErro as e:
        print(str(e), file=sys.stderr)
        return 1
    try:
        cm = _montar_cm(agente, pasta)
    except contexto.AgenteNaoEncontrado as e:
        print(mensagens.agente_nao_encontrado(e.agente, e.disponiveis), file=sys.stderr)
        return 1
    lanc = adapters.get(cliente).renderizar(cm)
    try:
        _materializar(lanc, pasta)
    except conflito.ConflitoErro as e:
        print(str(e), file=sys.stderr)
        return 1
    try:
        launch.lancar(cliente, pasta, env=lanc.env_vars or None, args=lanc.extra_args or None)
    except launch.ClienteNaoEncontrado as e:
        print(mensagens.cliente_nao_encontrado(e.cliente), file=sys.stderr)
        return 1
    except launch.ClienteNaoExecutavel as e:
        print(mensagens.cliente_nao_executavel(e.cliente, e.binpath), file=sys.stderr)
        return 1
    return 0  # alcançado só quando lancar é monkeypatched (Unix real: execvpe substitui)
