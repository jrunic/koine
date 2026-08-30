import argparse
import os
import pathlib
import platform
import shutil
import subprocess
import sys

from koine import (
    adapters,
    agente as _agente,
    atualizar as _atualizar,
    bootstrap as _bootstrap,
    canonica,
    conflito,
    contexto,
    escrita,
    estoque,
    ficha,
    frontmatter,
    indice,
    instantaneo as _instantaneo,
    instalar as _instalar,
    launch,
    mensagens,
    paseo,
    pasta as pasta_mod,
    pathenv,
    paths,
    prerequisitos,
    saida as _saida,
    schema,
    skills,
    validar as _validar,
    wrappers,
)
from koine._version import __version__

SUBCOMANDOS = {"versao", "instalar", "instalar-habilidades", "gerar", "mostrar",
               "validar", "atualizar", "definir-agente", "paseo-info"}


def main(argv: list[str] | None = None) -> int:
    # Antes de qualquer print: num stdout não-console do Windows o encoding é
    # cp1252, e o primeiro símbolo das mensagens abortaria o comando.
    _saida.preparar(sys.stdout, sys.stderr)
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("uso: koine <cliente|subcomando> ...\n"
              "subcomandos: instalar, instalar-habilidades, gerar, mostrar, "
              "validar, atualizar, paseo-info, versao", file=sys.stderr)
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
        if primeiro == "validar":
            return _cmd_validar(argv[1:])
        if primeiro == "atualizar":
            return _cmd_atualizar(argv[1:])
        if primeiro == "definir-agente":
            return _cmd_definir_agente(argv[1:])
        if primeiro == "paseo-info":
            return _cmd_paseo_info(argv[1:])
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
    p.add_argument("--para", default=None,
                   help="harness para instalar as skills; `todos` instala em "
                        "todos os detectados e `nenhum` pula a etapa")
    # O modo era INFERIDO por isatty. Inferência é o que trava automação rodada
    # de dentro de um terminal: o comando para num prompt e fica pendurado sem
    # erro. A flag decide, o terminal não.
    p.add_argument("--nao-interativo", action="store_true",
                   help="não pergunta nada; usa os defaults de cada decisão")
    p.add_argument("--pasta-canonica", default=None,
                   help="pasta canônica para as sessões com o Hermes (default: ~/koine)")
    p.add_argument("--contexto-canonico", choices=("preservar", "sobrescrever"),
                   default=None,
                   help="o que fazer com um CONTEXTO.md divergente na pasta canônica")
    ns = p.parse_args(args)

    if ns.para and ns.para not in ("todos", "nenhum") and ns.para not in skills.HARNESS_SKILLS:
        print(mensagens.harness_desconhecido(ns.para, sorted(skills.HARNESS_SKILLS)),
              file=sys.stderr)
        return 1

    vault_src = ns.vault or _localizar_vault()
    trocas, preservados = _instalar.extrair(vault_src, __version__, force=ns.force)
    for dest, bak in trocas:
        print(f"~ {os.path.basename(dest)} atualizado — sua versão anterior em {bak}")
    if preservados and not ns.force:
        print("Arquivos seus preservados (use --force para sobrescrever):")
        for d in preservados:
            print("  !", d)
    bindir = ns.bin or _bin_padrao()
    pyz = ns.pyz or _pyz_padrao()
    # sys.executable = interpretador que rodou `instalar` (>=3.10 garantido);
    # bakear absoluto no wrapper evita `python3` puro pegar um Python antigo.
    wrappers.gerar(bindir, pyz, sys.executable)
    if sys.platform == "win32":
        # A pasta entra no PATH DEPOIS de existir e ter os wrappers: PATH
        # apontando para pasta vazia é pior que PATH sem a pasta.
        _status_path = pathenv.garantir(bindir)
        print(mensagens.path_resultado(_status_path, bindir, pathenv.na_sessao(bindir)),
              end="")
    # espelha term.IsTerminal(stdin) do Go (instalar.go:61) — e a flag vence
    interativo = sys.stdin.isatty() and not ns.nao_interativo
    canonica.configurar(vault_src, interativo=interativo,
                        pasta_escolhida=ns.pasta_canonica or "",
                        contexto=ns.contexto_canonico or "")
    try:
        _instalar_com_deteccao(ns.para, interativo)
    except (OSError, ValueError) as e:
        # degradação graciosa, instalar.go:68-70 — skills falhando não aborta
        print(f"aviso: skills: {e}", file=sys.stderr)
    print("Instalação concluída.")
    if sys.platform == "win32":
        # Informacional, sempre: o problema aparece na primeira sessão, e a
        # instalação é onde o usuário ainda está prestando atenção. Não bloqueia
        # e não pergunta — relatório que trava o install é pior que nenhum.
        achados = prerequisitos.avaliar(skills.detectar_harnesses(),
                                        arquitetura=platform.machine(),
                                        pasta_codex=prerequisitos.codex_dir())
        print(mensagens.relatorio_prerequisitos(achados, platform.machine()), end="")
    # mensagem final SEMPRE imprime, mesmo com skills falhando (instalar.go:72-83)
    print(mensagens.final_instalar(), end="")
    return 0


def _instalar_com_deteccao(para: str | None, interativo: bool) -> None:
    """Porta de instalarComDeteccao (instalar.go:91-124): detecta harnesses no
    PATH e instala skills com confirmação. `para` dado → instala sem prompt;
    não-interativo → apenas informa."""
    print("\nInstalando skills de harness:")
    if para == "nenhum":
        print("  → Pulado por --para nenhum.")
        return
    if para and para != "todos":
        _instalar_skills_e_imprimir(para, __version__)
        return
    detectados = skills.detectar_harnesses()
    if para == "todos":
        if not detectados:
            print(mensagens.orientativa_sem_harness(), end="")
            return
        for h in detectados:
            try:
                _instalar_skills_e_imprimir(h, __version__)
            except (OSError, ValueError) as e:
                print(f"  aviso: {e}", file=sys.stderr)
        return
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
                _instalar_skills_e_imprimir(h, __version__)
            except (OSError, ValueError) as e:
                print(f"  aviso: {e}", file=sys.stderr)  # instalar.go:116-118
        else:
            print(f"  → Pulado. Para instalar depois: koine instalar-habilidades --para={h}")


def _instalar_skills_e_imprimir(h: str, versao: str) -> None:
    # espelha instalarEImprimir (instalar_habilidades.go:150-167), com a
    # política nova: divergente é atualizado e o backup é anunciado.
    criadas, existentes, atualizadas = skills.instalar_habilidades_detalhado(h, versao)
    home = str(pathlib.Path.home())
    print(f"  Skills para {h} ({os.path.join(home, *skills.HARNESS_SKILLS[h].split('/'))}):")
    for n in criadas:
        print(f"    + {n}")
    for n in existentes:
        print(f"    = {n}")
    for n, bak in atualizadas:
        print(f"    ~ {n} atualizada — sua versão anterior em {bak}")
    if not criadas and not existentes and not atualizadas:
        print("    (nenhuma skill kn-* encontrada em vault)")


def _cmd_definir_agente(args: list[str]) -> int:
    p = argparse.ArgumentParser(prog="koine definir-agente")
    p.add_argument("nome")
    p.add_argument("pasta", nargs="?", default="")
    p.add_argument("--default", action="store_true",
                   help="grava como agente default do usuário, em vez da pasta")
    ns = p.parse_args(args)

    if ns.default:
        alvo = contexto._achar_usuario_opcional(paths.config_dir())
        campo = _agente.CAMPO_DEFAULT
        if not alvo:
            print("Erro: não encontrei o seu arquivo de usuário em "
                  f"{paths.config_dir()} — rode `koine instalar` e "
                  "`/kn-01-recebe-usuario` primeiro.", file=sys.stderr)
            return 1
    else:
        try:
            alvo = os.path.join(pasta_mod.resolver(ns.pasta), "CONTEXTO.md")
        except pasta_mod.ResolucaoErro as e:   # o launch já captura; herdar
            print(str(e), file=sys.stderr)
            return 1
        campo = _agente.CAMPO_PASTA

    if ficha.definir_campo_arquivo(alvo, campo, ns.nome):
        print(f"{campo}: {ns.nome} → {alvo}")
        return 0
    # o mecanismo não escreve em três casos, e cada um tem conselho próprio
    print(f"Nada a gravar em {alvo}. Ou o valor já era esse, ou o arquivo não "
          "tem ficha (o bloco `---` no topo), ou está somente-leitura.",
          file=sys.stderr)
    return 1


def _cmd_instalar_habilidades(args: list[str]) -> int:
    p = argparse.ArgumentParser(prog="koine instalar-habilidades")
    p.add_argument("--para", required=True)
    p.add_argument("--force", action="store_true",
                   help="não é mais necessário: skill divergente já é atualizada")
    ns = p.parse_args(args)
    if ns.force:
        # aceita em vez de recusar: era o único jeito de atualizar skill, e
        # quem a tem no dedo receberia `unrecognized arguments` justamente no
        # comando que roda para se atualizar. Avisa — não é no-op silencioso.
        print("aviso: --force não é mais necessário — skill divergente já é "
              "atualizada, com a sua versão guardada no cache.", file=sys.stderr)
    atualizadas = skills.instalar_habilidades(ns.para, __version__)
    for n, bak in atualizadas:
        print(f"~ {n} atualizada — sua versão anterior em {bak}")
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


def _montar_cm(agente: str, pasta: str,
               canal: bool = False) -> contexto.ContextoMontado:
    ctx_path = os.path.join(pasta, "CONTEXTO.md")
    fm, _ = frontmatter.ler_arquivo(ctx_path, normalizar_disco=True)
    # bootstrap e pasta incompleta não têm escopo nem índices; resolver trata os ramos.
    if not fm.get("bootstrap") and fm.get("escopo"):
        try:
            # índices antes do render (o adapter os referencia)
            escopo_fm, _ = frontmatter.ler_arquivo(
                contexto.resolver_escopo_path(paths.config_dir(), fm["escopo"]),
                normalizar_disco=True)
        except contexto.EscopoNaoEncontrado:
            # Sem cadastro não há pasta de referências, e portanto não há índice
            # a gerar. Quem decide a política é `resolver`, logo abaixo: no
            # terminal ele levanta de novo, com a lista; no canal devolve a
            # sessão de bootstrap. Engolir aqui sem reencaminhar seria o silêncio.
            if not canal:
                raise
        else:
            refs = paths.resolver_tagged(
                schema.Escopo.from_fm(escopo_fm).pasta_referencias)
            indice.gerar(refs, fm.get("dominios", []))
    cm = contexto.resolver(agente, pasta, canal=canal)
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


def _cmd_validar(args: list[str]) -> int:
    """Varre o frontmatter da config do usuário e da pasta dada (default: a
    atual). Sem `--corrigir`, não escreve nada. Sai 1 quando sobra algo a
    corrigir — serve de gate em script."""
    cfg = paths.config_dir()
    alvos = [a for a in args if not a.startswith("-")] or [os.getcwd()]
    # a pasta-referências do escopo mora fora da config e é onde vivem as
    # referências da /kn-11 — varrer só a config deixaria de fora justo elas
    refs = [r for r in (_validar.refs_do_escopo(a, cfg) for a in alvos) if r]
    achados = _validar.varrer([cfg] + alvos + refs)
    if "--corrigir" not in args:
        print(_validar.relatorio(achados), end="")
        return 1 if achados else 0
    corrigidos, pendentes = _validar.corrigir(achados)
    print(_validar.relatorio_correcao(corrigidos, pendentes), end="")
    return 1 if pendentes else 0


def _cmd_gerar(args: list[str]) -> int:
    # `--para` é consumido AQUI, não por _separar_args: aquela gramática é a do
    # launch, onde o token sem hífen depois de uma flag é posicional do koine —
    # o valor de `--para` seria lido como pasta.
    cliente = "claude"
    if "--para" in args:
        i = args.index("--para")
        if i + 1 >= len(args):
            print("uso: koine gerar <agente> [pasta] [--para <cliente>]", file=sys.stderr)
            return 1
        cliente = args[i + 1]
        args = args[:i] + args[i + 2:]
    posicionais = [a for a in args if not a.startswith("-")]
    if cliente not in adapters.REGISTRY:
        print(mensagens.cliente_desconhecido(cliente, sorted(adapters.REGISTRY)),
              file=sys.stderr)
        return 1
    agente = posicionais[0] if posicionais else ""
    args = posicionais
    try:
        pasta = pasta_mod.resolver(args[1] if len(args) >= 2 else "")
    except pasta_mod.ResolucaoErro as e:
        print(str(e), file=sys.stderr)
        return 1
    if _bootstrap.classificar(pasta) in (
            _bootstrap.AUSENTE, _bootstrap.VAZIO, _bootstrap.INCOMPLETO,
            _bootstrap.MALFORMADO):
        erro = _bootstrap.erro_frontmatter(pasta)
        print(mensagens.frontmatter_invalido(erro) if erro
              else mensagens.pasta_sem_contexto_admin(pasta), file=sys.stderr)
        return 1
    try:
        cm = _montar_cm(agente, pasta)
    except contexto.AgenteNaoEncontrado as e:
        print(mensagens.agente_nao_encontrado(e.agente, e.disponiveis), file=sys.stderr)
        return 1
    except frontmatter.FrontmatterInvalido as e:
        print(mensagens.frontmatter_invalido(e), file=sys.stderr)
        return 1
    except contexto.EscopoNaoEncontrado as e:
        print(mensagens.escopo_nao_encontrado(e.escopo, e.disponiveis), file=sys.stderr)
        return 1
    arquivo, conteudo = adapters.get(cliente).renderizar_para_pasta(cm)
    # marca de INTENÇÃO: no modo skills a pasta é a única via de entrega, e um
    # launch na mesma pasta não pode apagar o que o usuário mandou gerar
    conteudo = escrita.marcar_a_pedido(conteudo)
    destino = os.path.join(pasta, arquivo)
    try:
        # MESMA política do launch: arquivo do usuário no caminho vira .bak, e
        # symlink/diretório abortam. O `gerar` escrevia direto — em 27/08/2026
        # substituiu um CLAUDE.md pessoal sem backup e ainda imprimiu os bytes.
        escrita.gravar(destino, conteudo)
    except escrita.ConflitoErro as e:
        print(str(e), file=sys.stderr)
        return 1
    print(f"Escrito {destino} ({len(conteudo.encode('utf-8'))} bytes)")
    return 0


def _cmd_mostrar(args: list[str]) -> int:
    # Agente opcional, como no launch: `mostrar` sem posicional descobre o que a
    # pasta atual vai abrir. A pasta segue sendo o segundo posicional (arg cru,
    # sem alias) — gramática igual à do launch, de propósito: duas gramáticas de
    # pasta lado a lado é o tipo de divergência que este comando existe para
    # não ter.
    agente = args[0] if args else ""
    alvo = args[1] if len(args) >= 2 else os.getcwd()
    # Pasta incompleta COM foto: o launch vai curar. Verificação não escreve,
    # então aqui só se anuncia — recusar daria a entender que a sessão não abre.
    if _bootstrap.classificar(alvo) == _bootstrap.INCOMPLETO:
        foto = _instantaneo.recuperar(alvo)
        if foto:
            print(mensagens.ficha_sera_reposta(alvo, foto.quando))
            return 0
    # alvo NÃO resolve alias — comportamento congelado de `mostrar` (arg cru)
    if _bootstrap.classificar(alvo) in (
            _bootstrap.AUSENTE, _bootstrap.VAZIO, _bootstrap.INCOMPLETO,
            _bootstrap.MALFORMADO):
        erro = _bootstrap.erro_frontmatter(alvo)
        print(mensagens.frontmatter_invalido(erro) if erro
              else mensagens.pasta_sem_contexto_admin(alvo), file=sys.stderr)
        return 1
    try:
        cm = _montar_cm(agente, alvo)
    except contexto.AgenteNaoEncontrado as e:
        print(mensagens.agente_nao_encontrado(e.agente, e.disponiveis), file=sys.stderr)
        return 1
    except frontmatter.FrontmatterInvalido as e:
        print(mensagens.frontmatter_invalido(e), file=sys.stderr)
        return 1
    except contexto.EscopoNaoEncontrado as e:
        print(mensagens.escopo_nao_encontrado(e.escopo, e.disponiveis), file=sys.stderr)
        return 1
    _, conteudo = adapters.get("claude").renderizar_para_pasta(cm)
    # A linha do agente vem antes do conteúdo: é a resposta de "qual agente esta
    # pasta abre?", e sai do MESMO cm que o launch monta — é o que impede a
    # ferramenta que avisa de divergir da que abre.
    print(f"Agente: {os.path.basename(cm.agente_path)[:-3]}")
    if cm.agente_ausente:
        print(f"  (a pasta declara '{cm.agente_ausente}', que não existe — "
              f"a sessão abriria com o Hermes)")
    print(conteudo, end="")
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
        # Pai segura o alvo_pyz; delega ao filho DESTACADO. O finalizador roda o
        # CÓDIGO ATUAL (cópia do pyz vigente), NÃO o alvo baixado — o alvo pode não
        # ter `atualizar --finalizar` (ex.: downgrade para versão sem a feature).
        # Rodando de uma cópia neutra, o filho não segura nem o staged nem o dist,
        # então o os.replace(staged → dist) funciona. stdio para log: processo
        # destacado não tem console e print() lançaria WinError 6.
        finalizador = os.path.join(staging, "finalizador.pyz")
        shutil.copyfile(alvo_pyz, finalizador)
        logpath = os.path.join(paths.cache_dir(), "atualizar.log")
        os.makedirs(os.path.dirname(logpath), exist_ok=True)
        logf = open(logpath, "w", encoding="utf-8")
        DETACHED = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        subprocess.Popen(
            [sys.executable, finalizador, "atualizar", "--finalizar",
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


def _separar_args(args: list[str]) -> tuple[list[str], list[str]]:
    """Separa os posicionais do koine (agente, pasta) dos args repassados ao
    cliente IA. Tudo após `--` é repassado literal (útil p/ flags com valor,
    ex.: `-- --model sonnet`). Antes de `--`, tokens com prefixo `-` são flags
    do cliente (ex.: `kn-claude hermes . --chrome`); os demais são posicionais.
    O usuário escolhe quando ligar cada flag — a lib só repassa."""
    if "--" in args:
        i = args.index("--")
        antes, passa = args[:i], args[i + 1:]
    else:
        antes, passa = args, []
    posicionais = [a for a in antes if not a.startswith("-")]
    flags = [a for a in antes if a.startswith("-")]
    return posicionais, flags + passa


def _cmd_paseo_info(args: list[str]) -> int:
    """Matriz de rotas pelo orquestrador, em formato de máquina.

    É o contrato com a skill que escreve os providers: ela lê daqui o nome do
    wrapper e o `extends` do entry, em vez de carregar uma cópia da tabela —
    que envelheceria sozinha quando entrasse cliente novo, e cujo sintoma seria
    um provider que abre sessão sem contexto e sem erro.
    """
    import json
    dados = {}
    for cliente in paseo.com_rota():
        r = paseo.rota(cliente)
        dados[cliente] = {"wrapper": paseo.wrapper_de(cliente),
                          "provider": paseo.entry_de(cliente),
                          "provider_hermes": paseo.entry_hermes_de(cliente),
                          "extends": r.extends, "args": list(r.args)}
    if "--json" in args:
        print(json.dumps(dados, indent=2, ensure_ascii=False))
        return 0
    for cliente, info in dados.items():
        print(f"{cliente:10} {info['provider']:14} {info['provider_hermes']:22} "
              f"{info['wrapper']:22} extends={info['extends']}")
    return 0


def _lancar_avisando_sem_contexto(cliente: str, pasta: str,
                                  extras_usuario: list[str]) -> int:
    """Sobe a sessão com a instrução do vault, sem tocar na pasta.

    Não escrever não pode virar silêncio: sessão que sobe sem contexto e sem
    aviso é indistinguível de uma sessão normal, e o usuário só descobre quando
    as respostas saem genéricas.
    """
    cm = contexto.resolver("", pasta, sem_contexto=True)
    cm.pasta_abs = pasta
    lanc = adapters.get(cliente).renderizar(cm)
    _materializar(lanc, pasta)
    args_cliente = (lanc.extra_args or []) + extras_usuario
    launch.lancar(cliente, pasta, env=lanc.env_vars or None, args=args_cliente or None)
    return 0


def _rodar_cliente(cliente: str, args: list[str]) -> int:
    # `--canal-paseo` é consumido AQUI, não por _separar_args: naquela gramática
    # todo token com hífen é flag do cliente, e a flag chegaria ao processo
    # lançado. Mesmo motivo pelo qual o `--para` do `gerar` é consumido antes.
    canal_paseo = "--canal-paseo" in args
    if canal_paseo:
        args = [a for a in args if a != "--canal-paseo"]
    # Subcomando que o cliente exige para falar o protocolo do orquestrador. Vem
    # ANTES de tudo: é subcomando, não flag. Calculado uma vez porque os dois
    # ramos de lançamento (pasta válida e pasta sem contexto) precisam dele — e
    # a sondagem do orquestrador roda justamente do segundo.
    prefixo = []
    if canal_paseo:
        _rota = paseo.rota(cliente)
        if _rota is not None:
            prefixo = list(_rota.args)
    posicionais, extras_usuario = _separar_args(args)
    # 0 posicionais: a pasta resolve o agente (é a invocação dos providers
    # remotos, que são genéricos e fixos). 1: é AGENTE, efêmero. 2: agente +
    # pasta. Regra fixa, não adivinhação — `kn-<cliente> <pasta>` sozinho cai em
    # "agente inexistente" com a lista, que é autocorretivo.
    agente = posicionais[0] if posicionais else ""
    if canal_paseo and not agente:
        # O provider do Paseo não tem como passar posicional: o array `command`
        # descarta argumentos extras no spawn (medido em 29/08/2026). A variável
        # é o único canal, e entra na MESMA posição do posicional — pedido do
        # chamador, efêmero, que não persiste na pasta.
        # Vazia conta como ausente: nas sondagens ela chega de forma
        # inconsistente, e ausência é caminho normal, nunca erro.
        agente = os.environ.get("KOINE_AGENTE", "").strip()
    try:
        pasta = pasta_mod.resolver(posicionais[1] if len(posicionais) >= 2 else "")
    except pasta_mod.ResolucaoErro as e:
        print(str(e), file=sys.stderr)
        return 1
    # auto-guiar: pasta de sessão sem CONTEXTO.md válido (só o launch trata).
    estado = _bootstrap.classificar(pasta)
    if canal_paseo and estado in (_bootstrap.AUSENTE, _bootstrap.VAZIO,
                                  _bootstrap.INCOMPLETO, _bootstrap.MALFORMADO):
        # Nada é escrito, e nada aborta. Escrever: as sondagens do orquestrador
        # rodam com o cwd de onde ele subiu, e o auto-guiar materializaria
        # bootstrap em pasta que ninguém escolheu (medido em 29/08/2026).
        # Abortar: provider que sai com código não-zero é beco sem saída, e como
        # o orquestrador apresenta isso NÃO foi medido — a escolha conservadora
        # é subir avisando.
        return _lancar_avisando_sem_contexto(cliente, pasta, prefixo + extras_usuario)
    if estado in (_bootstrap.AUSENTE, _bootstrap.VAZIO):
        if not _bootstrap.usuario_onboarded(paths.config_dir()):
            print(mensagens.pasta_sem_contexto_nao_onboarded(cliente), file=sys.stderr)
            return 1
        ctx = os.path.join(pasta, "CONTEXTO.md")
        if os.path.islink(ctx) or os.path.isdir(ctx):
            print(mensagens.contexto_conflito(ctx), file=sys.stderr)
            return 1
        with open(ctx, "w", encoding="utf-8") as f:
            f.write(_bootstrap.CONTEXTO_CONFIGURA_PASTA)
        # resolver vê `bootstrap: true` e força Hermes — o agente pedido é ignorado.
    elif estado == _bootstrap.INCOMPLETO:
        # A ficha pode ter sumido no fechamento da sessão anterior. Se há foto
        # desta pasta, ela volta ANTES de qualquer coisa — e o estado é
        # RE-MEDIDO: sem isso, a sessão seguiria tratada como incompleta mesmo
        # com a ficha de volta, e o usuário receberia o Hermes com instrução de
        # consertar uma pasta que já está consertada.
        foto = _instantaneo.recuperar(pasta)
        if foto and ficha.repor_bloco(os.path.join(pasta, "CONTEXTO.md"), foto.bloco):
            print(mensagens.ficha_reposta(pasta, foto.quando), file=sys.stderr)
            estado = _bootstrap.classificar(pasta)
    if estado == _bootstrap.INCOMPLETO:
        # CONTEXTO.md do usuário sem `escopo:`, e sem foto que o cure. Não se
        # escreve sobre ele: é dele. `contexto.resolver` devolve CM de bootstrap
        # com a instrução do vault + o arquivo original, e o Hermes completa via
        # /kn-02 Fluxo 3b.
        if not _bootstrap.usuario_onboarded(paths.config_dir()):
            print(mensagens.pasta_sem_contexto_nao_onboarded(cliente), file=sys.stderr)
            return 1
    elif estado == _bootstrap.MALFORMADO:
        erro = _bootstrap.erro_frontmatter(pasta)
        print(mensagens.frontmatter_invalido(erro) if erro
              else mensagens.contexto_ilegivel(pasta), file=sys.stderr)
        return 1
    try:
        cm = _montar_cm(agente, pasta, canal=canal_paseo)
    except contexto.AgenteNaoEncontrado as e:
        print(mensagens.agente_nao_encontrado(e.agente, e.disponiveis), file=sys.stderr)
        return 1
    except frontmatter.FrontmatterInvalido as e:
        print(mensagens.frontmatter_invalido(e), file=sys.stderr)
        return 1
    except contexto.EscopoNaoEncontrado as e:
        print(mensagens.escopo_nao_encontrado(e.escopo, e.disponiveis), file=sys.stderr)
        return 1
    # Agente declarado num arquivo e inexistente: com TTY o Hermes conduz a
    # correção (a instrução já veio no cm); sem TTY não há a quem perguntar, e
    # subir em silêncio faria a sessão remota rodar com o agente errado sem
    # ninguém perceber. Detecção por isatty, agnóstica de cliente — `--print` é
    # vocabulário do Claude Code, não dos outros quatro.
    #
    # O canal é a exceção, e não por conveniência: ali NUNCA há tty, e mesmo
    # assim há gente do outro lado — a pessoa está no celular. O isatty, que
    # aqui é procuração para "há alguém para avisar", erra o sinal; quem avisa
    # é a instrução que o `cm` já carrega (jd-task #709).
    if cm.agente_ausente and not canal_paseo and not sys.stdin.isatty():
        print(mensagens.agente_declarado_inexistente(cm.agente_ausente),
              file=sys.stderr)
        return 1
    # Foto da ficha DEPOIS de montar o contexto: é lá que a normalização roda, e
    # fotografar antes guardaria um bloco torto — o defeito atravessaria a foto.
    if estado == _bootstrap.VALIDO:
        _instantaneo.guardar(pasta, _bootstrap.bloco_do_contexto(pasta))
    # Estoque do mecanismo antigo: sai ANTES de materializar. É o único ponto do
    # Koine que remove arquivo da pasta, e por isso só alcança o que carrega o
    # nosso marcador (ou é um dos dois symlinks que nós criávamos).
    for removido in estoque.limpar(pasta):
        print(f"aviso: {os.path.basename(removido)} do mecanismo anterior removido "
              f"— o contexto agora é entregue fora da pasta", file=sys.stderr)
    lanc = adapters.get(cliente).renderizar(cm)
    try:
        _materializar(lanc, pasta)
    except conflito.ConflitoErro as e:
        print(str(e), file=sys.stderr)
        return 1
    args_cliente = prefixo + (lanc.extra_args or []) + extras_usuario
    if sys.platform == "win32":
        # Uma linha: o relatório completo é da instalação. Aqui é o que o usuário
        # precisa para não perder tempo — e a sessão SOBE assim mesmo, porque sem
        # shell ela ainda entrega contexto e leitura de arquivos. Vale para os
        # DOIS códigos: o claude sem Git Bash também não tem shell, e é o único
        # com remédio, então é o aviso mais útil dos dois.
        achado = prerequisitos.avaliar_cliente(cliente)
        if achado is not None:
            print(mensagens.aviso_launch_sem_shell(cliente, achado.codigo),
                  file=sys.stderr)
    try:
        launch.lancar(cliente, pasta, env=lanc.env_vars or None, args=args_cliente or None)
    except launch.ClienteNaoEncontrado as e:
        print(mensagens.cliente_nao_encontrado(e.cliente), file=sys.stderr)
        return 1
    except launch.ClienteNaoExecutavel as e:
        print(mensagens.cliente_nao_executavel(e.cliente, e.binpath), file=sys.stderr)
        return 1
    return 0  # alcançado só quando lancar é monkeypatched (Unix real: execvpe substitui)
