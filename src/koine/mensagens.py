"""Mensagens de onboarding do `instalar`.

Porta de cmd/kn-agente/mensagem_orientativa.go (integral, byte-fiel — exceto
a troca declarada `kn-agente instalar` → `koine instalar` no rodapé) e da
mensagem final de cmd/kn-agente/instalar.go:73-86.
"""

import os
import platform
import shutil


def _os_atual() -> str:
    # espelha runtime.GOOS (lookupOS do Go)
    return {"Darwin": "darwin", "Linux": "linux", "Windows": "windows"}.get(
        platform.system(), platform.system().lower())


def _tem_binario(nome: str) -> bool:
    return shutil.which(nome) is not None


def orientativa_sem_harness() -> str:
    """Porta 1:1 de mensagemOrientativaSemHarness: cabeçalho + bloco Node
    (se ausente; texto por OS) + bloco Brew (darwin sem brew) + 4 blocos de
    cliente + rodapé."""
    os_ = _os_atual()
    node_ausente = not _tem_binario("node")
    brew_ausente = os_ == "darwin" and not _tem_binario("brew")

    partes = [
        "  (nenhum cliente IA detectado no PATH)\n",
        "\n",
        "  Koine funciona junto com um cliente IA terminal. Antes de\n",
        "  escolher um cliente, confira os pré-requisitos:\n",
        "\n",
    ]
    if node_ausente:
        partes.append(_bloco_node_ausente(os_))
        partes.append("\n")
    if brew_ausente:
        partes.append(_bloco_brew_ausente())
        partes.append("\n")
    partes.append("  Clientes IA suportados (escolha um):\n")
    partes.append("\n")
    partes.append(_bloco_cliente_claude(os_))
    partes.append("\n")
    partes.append(_bloco_cliente_antigravity(os_))
    partes.append("\n")
    partes.append(_bloco_cliente_copilot(os_))
    partes.append("\n")
    partes.append(_bloco_cliente_opencode(os_))
    partes.append("\n")
    partes.append("  Depois de instalar um cliente, rode `koine instalar` novamente —\n")
    partes.append("  ele detecta automaticamente.\n")
    return "".join(partes)


def _bloco_node_ausente(os_: str) -> str:
    b = [
        "  ⚠️  Node.js não encontrado\n",
        "\n",
        "     Vários clientes IA são instalados via npm (Claude Code, Copilot).\n",
        "     Como instalar:\n",
    ]
    if os_ == "darwin":
        b.append("       brew install node    (recomendado em macOS)\n")
        b.append("       ou baixe de https://nodejs.org/\n")
    elif os_ == "linux":
        b.append("       via gerenciador do seu sistema (apt, dnf, pacman, apk)\n")
        b.append("       ou baixe de https://nodejs.org/\n")
    elif os_ == "windows":
        b.append("       baixe e instale de https://nodejs.org/\n")
    else:
        b.append("       https://nodejs.org/\n")
    b.append("\n")
    b.append("     Documentação:  https://nodejs.org/\n")
    return "".join(b)


def _bloco_brew_ausente() -> str:
    return (
        "  💡 Homebrew não encontrado (macOS)\n"
        "\n"
        "     Gerenciador de pacotes recomendado no macOS — instala muitos\n"
        "     clientes IA com um comando.\n"
        "     Como instalar:\n"
        "       /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"\n"
        "\n"
        "     Documentação:  https://brew.sh/\n"
    )


def _bloco_cliente_claude(os_: str) -> str:
    b = ["  • Claude Code (Anthropic)\n"]
    if os_ == "darwin":
        b.append("    Como instalar:  brew install --cask claude-code\n")
        b.append("                    (ou: npm install -g @anthropic-ai/claude-code)\n")
    else:
        b.append("    Como instalar:  npm install -g @anthropic-ai/claude-code\n")
    b.append("    Docs:           https://docs.claude.com/en/docs/claude-code/setup\n")
    return "".join(b)


def _bloco_cliente_antigravity(os_: str) -> str:
    b = ["  • Antigravity (Google)\n"]
    if os_ == "windows":
        b.append("    Como instalar:  irm https://antigravity.google/cli/install.ps1 | iex\n")
    else:
        b.append("    Como instalar:  curl -fsSL https://antigravity.google/cli/install.sh | bash\n")
    b.append("    Docs:           https://antigravity.google/docs/cli-install\n")
    return "".join(b)


def _bloco_cliente_copilot(os_: str) -> str:
    b = ["  • GitHub Copilot CLI\n"]
    if os_ == "darwin":
        b.append("    Como instalar:  brew install --cask copilot-cli\n")
        b.append("                    (ou: npm install -g @github/copilot)\n")
    else:
        b.append("    Como instalar:  npm install -g @github/copilot\n")
    b.append("    Docs:           https://docs.github.com/copilot/copilot-cli\n")
    return "".join(b)


def _bloco_cliente_opencode(os_: str) -> str:
    b = ["  • OpenCode\n"]
    if os_ == "windows":
        b.append("    Como instalar:  npm install -g opencode-ai\n")
    else:
        b.append("    Como instalar:  curl -fsSL https://opencode.ai/install | bash\n")
    b.append("    Docs:           https://opencode.ai/docs\n")
    return "".join(b)


def cliente_nao_encontrado(cliente: str) -> str:
    """Cliente NÃO está no PATH (shutil.which devolveu None). Aqui sim o
    diagnóstico é 'não instalado ou fora do PATH'. Guia por OS."""
    os_ = _os_atual()
    b = [
        f"  ✗ cliente '{cliente}' não encontrado no PATH\n",
        "\n",
        f"    Ou o '{cliente}' não está instalado, ou a pasta dele não está no PATH.\n",
        "\n",
        "    Diagnostique no MESMO terminal:\n",
    ]
    if os_ == "windows":
        b += [
            f"      where {cliente}\n",
            "        • nada listado  → não instalado, ou a pasta não está no PATH\n",
            f"        • lista caminho → o '{cliente}' está no PATH (reabra o terminal e tente de novo)\n",
            "\n",
            "    Se a pasta do Koine é que está fora do PATH, o próprio instalador\n",
            "    resolve — rode `koine instalar` de novo e reabra o terminal.\n",
            "\n",
            "    Para a pasta de OUTRO programa, sem administrador:\n",
            "      cmd:  rundll32 sysdm.cpl,EditEnvironmentVariables\n",
            "            em Variáveis de usuário, edite Path e acrescente <PASTA>\n",
            "    Depois reabra o terminal.\n",
        ]
    else:
        b += [
            f"      command -v {cliente}\n",
            f"        • vazio → instale o '{cliente}' ou adicione a pasta dele ao PATH\n",
            "\n",
            "    Adicionar ao PATH (no seu ~/.zshrc ou ~/.bashrc), trocando <PASTA>:\n",
            '      export PATH="<PASTA>:$PATH"\n',
            "    Depois reabra o terminal.\n",
        ]
    return "".join(b)


def agente_nao_encontrado(agente: str, disponiveis: list[str]) -> str:
    """Nenhum agente casa com o nome pedido (contexto.AgenteNaoEncontrado).
    Lista os disponíveis para o usuário corrigir o nome."""
    lista = "\n".join(f"      • {d}" for d in disponiveis) if disponiveis \
        else "      (nenhum agente cadastrado — rode /kn-03-cria-agente)"
    return (
        f"  ✗ agente '{agente}' não encontrado\n"
        "\n"
        "    Agentes disponíveis:\n"
        f"{lista}\n"
    )


def cliente_nao_executavel(cliente: str, binpath: str) -> str:
    """Cliente FOI encontrado, mas o SO recusou executá-lo (WinError 193 & cia.).
    NÃO é PATH — o arquivo existe. Aponta o caminho achado e como corrigir."""
    return (
        f"  ✗ cliente '{cliente}' encontrado, mas o Windows não conseguiu executá-lo\n"
        "\n"
        "    Caminho resolvido:\n"
        f"      {binpath}\n"
        "\n"
        "    Este NÃO é um erro de PATH — o comando foi encontrado. O arquivo acima\n"
        "    não é um executável Win32 válido (WinError 193): normalmente é um shim\n"
        f"    ou atalho inválido do '{cliente}', não o executável real.\n"
        "\n"
        "    Como investigar (mostra TODAS as entradas no PATH):\n"
        f"      where {cliente}\n"
        f"    Prefira a entrada .exe ou .cmd real do '{cliente}' e ajuste o PATH para\n"
        "    ela vir primeiro. Se persistir, reinstale o cliente e reabra o terminal.\n"
    )


def pasta_sem_contexto_nao_onboarded(cliente: str) -> str:
    """Launch numa pasta sem CONTEXTO.md e SEM usuário configurado (nunca fez
    onboarding). Não roda /kn-01 numa pasta aleatória — redireciona ao setup
    canônico, onde o onboarding tem lugar próprio (~/koine)."""
    return (
        "  Esta pasta não tem um CONTEXTO.md configurado, e você ainda não fez\n"
        "  o onboarding do Koine.\n"
        "\n"
        "  Configure o Koine primeiro (uma vez só):\n"
        "    koine instalar\n"
        f"    kn-{cliente} hermes koine\n"
        "\n"
        "  Dentro dessa sessão, o Hermes conduz o onboarding. Depois volte a esta\n"
        "  pasta e abra a sessão normalmente.\n"
    )


def pasta_sem_contexto_admin(pasta: str) -> str:
    """`gerar`/`mostrar` numa pasta sem CONTEXTO.md válido. Comandos
    administrativos não materializam nada — orientam a configurar via launch."""
    return (
        f"  Esta pasta não tem um CONTEXTO.md configurado:\n"
        f"    {pasta}\n"
        "\n"
        "  Para configurá-la, abra uma sessão aqui com o Hermes:\n"
        "    kn-claude hermes .\n"
        "  (troque `kn-claude` pelo wrapper do seu cliente: kn-agy, kn-copilot,\n"
        "  kn-opencode, kn-codex). O Hermes cria o CONTEXTO.md desta pasta.\n"
    )


def contexto_ilegivel(pasta: str) -> str:
    """CONTEXTO.md existe mas o Koine não conseguiu lê-lo (binário, permissão,
    encoding). Frontmatter só incompleto NÃO cai aqui — esse caso é auto-guiado
    pelo launch desde a v0.6.1."""
    return (
        f"  Não consegui ler o CONTEXTO.md desta pasta:\n"
        f"    {os.path.join(pasta, 'CONTEXTO.md')}\n"
        "\n"
        "  O arquivo existe, mas não é texto legível (binário, permissão negada\n"
        "  ou encoding inesperado). Confira o arquivo — o Koine não o alterou.\n"
    )


def indice_nao_gerado(refs: str, erro: OSError) -> str:
    """A pasta-referências não aceitou a escrita do índice — a sessão segue.

    A pista do OneDrive vai junto porque é a causa de produção: com Known Folder
    Move, `Documentos` aponta para o OneDrive no Explorer e o caminho físico do
    perfil vira casca vazia. Quem lê este aviso na máquina onde isso acontece
    precisa do palpite, não só do fato.
    """
    return (
        f"  ! índice do escopo não atualizado — {type(erro).__name__} em\n"
        f"    {refs}\n"
        "\n"
        "    A sessão abriu assim mesmo, com o índice que já estivesse lá (pode\n"
        "    estar desatualizado). As referências continuam no lugar; o que\n"
        "    falhou foi escrever o catálogo delas.\n"
        "\n"
        "    Se esta pasta está no OneDrive ou no Google Drive, confira o\n"
        "    caminho com `koine validar` — pasta redirecionada é a causa mais\n"
        "    comum, e o caminho real costuma ser outro.\n"
    )


def escopo_nao_encontrado(escopo: str, disponiveis: list[str]) -> str:
    """CONTEXTO.md aponta para um escopo que não existe em config/escopos.
    Erra-se o slug com facilidade; listar os cadastrados resolve na hora."""
    lista = "\n".join(f"      • {d}" for d in disponiveis) if disponiveis \
        else "      (nenhum escopo cadastrado — rode /kn-02-mantem-catalogo)"
    return (
        f"  ✗ escopo '{escopo}' não encontrado\n"
        "\n"
        "    O CONTEXTO.md desta pasta aponta para um escopo que não existe.\n"
        "    Escopos cadastrados:\n"
        f"{lista}\n"
        "\n"
        "    Corrija o campo `escopo:` do CONTEXTO.md, ou crie o escopo com\n"
        "    /kn-02-mantem-catalogo (fluxo escopo).\n"
    )


def frontmatter_invalido(erro) -> str:
    """YAML do frontmatter que nem o reparo automático salva (tab, indentação
    quebrada, bloco que não é `chave: valor`). Nomeia arquivo, linha e coluna —
    o usuário nunca viu YAML na vida e precisa saber onde pôr a mão."""
    local = erro.arquivo or "(frontmatter)"
    if erro.linha:
        local += f"\n    linha {erro.linha}" + (f", coluna {erro.coluna}" if erro.coluna else "")
    return (
        "  ✗ frontmatter inválido — não consegui ler o YAML do topo do arquivo:\n"
        f"    {local}\n"
        f"\n    Detalhe: {erro.motivo}\n"
        "\n"
        "    O frontmatter é o bloco entre `---` no começo do arquivo, e cada\n"
        "    linha é `chave: valor`. Causas comuns:\n"
        "      • TAB no lugar de espaços (YAML só aceita espaço)\n"
        "      • valor com `:` ou aspas soltas — cite entre aspas duplas:\n"
        '          descricao: "Vendas: meta e funil"\n'
        "      • linha sem `chave:` no começo\n"
    )


def contexto_conflito(ctx: str) -> str:
    """O CONTEXTO.md que seria materializado é um symlink ou diretório —
    escrever por cima perderia dado (ex.: symlink de sessão opencode/copilot)."""
    return (
        f"  Não consigo criar o CONTEXTO.md — o caminho já existe e não é um\n"
        f"  arquivo regular:\n"
        f"    {ctx}\n"
        "\n"
        "  É um symlink ou diretório. Resolva manualmente e tente de novo.\n"
    )


def final_instalar() -> str:
    # porta de instalar.go:72-83 (mensagem final do onboarding)
    return (
        "\nPara começar sua primeira sessão com Hermes:\n\n"
        "  kn-claude hermes koine\n\n"
        "Dentro da sessão, rode: /kn-01-recebe-usuario\n\n"
        "Se você usa outro cliente, troque o prefixo:\n"
        "  Antigravity:  kn-agy hermes koine\n"
        "  Copilot CLI:  kn-copilot hermes koine\n"
        "  OpenCode:     kn-opencode hermes koine\n"
        "  Codex CLI:    kn-codex hermes koine\n")


def atualizar_ja_recente(versao: str) -> str:
    return f"Koine já está na versão {versao}."


def agente_declarado_inexistente(nome: str) -> str:
    """Pasta (ou default do usuário) declara agente que não existe, e não há TTY
    para conduzir a correção. Com TTY o Hermes guia; aqui a sessão para, porque
    subir com o agente errado em silêncio é pior que não subir."""
    return (
        f"  ✗ a pasta declara o agente '{nome}', que não existe\n"
        "\n"
        "    A sessão não vai abrir com o agente errado sem avisar.\n"
        "\n"
        "    Corrija com um agente que exista:\n"
        f"      koine definir-agente <nome>\n"
        "\n"
        "    Para ver os que existem:  koine mostrar\n"
    )


def ficha_reposta(pasta: str, quando: str) -> str:
    """A ficha do CONTEXTO.md tinha sumido e foi reposta da foto da última sessão
    válida. O aviso existe para o sintoma continuar visível: se a reposição fosse
    silenciosa, ninguém perceberia que algo está comendo o frontmatter."""
    de_quando = f" (de {quando})" if quando else ""
    return (
        f"aviso: a ficha de {pasta}/CONTEXTO.md tinha sumido — repus a da última "
        f"sessão{de_quando}.\n"
        f"       O arquivo como estava ficou em CONTEXTO.md.bak, ao lado.\n"
    )


def ficha_sera_reposta(pasta: str, quando: str) -> str:
    """`mostrar` numa pasta cuja ficha sumiu, mas que tem foto. Verificação não
    escreve — então ele anuncia o que o launch vai fazer, em vez de recusar como
    se a sessão não fosse abrir."""
    de_quando = f" (de {quando})" if quando else ""
    return (f"A ficha deste CONTEXTO.md sumiu, mas há uma foto{de_quando}.\n"
            f"Abrir a sessão nesta pasta repõe a ficha automaticamente.\n")


def cliente_desconhecido(cliente: str, disponiveis: list[str]) -> str:
    return (f"cliente desconhecido: {cliente}\n"
            f"clientes disponíveis: {', '.join(disponiveis)}")


def harness_desconhecido(valor: str, disponiveis: list[str]) -> str:
    return (f"harness desconhecido: {valor}\n"
            f"harnesses: {', '.join(disponiveis)}\n"
            "use `todos` para instalar em todos os detectados, ou `nenhum` para pular")


_ARQUIVO_GIT = {"ARM64": "ARM64 Git for Windows Setup",
                "AMD64": "64-bit Git for Windows Setup"}


def relatorio_prerequisitos(achados, arquitetura=None) -> str:
    """O que vai funcionar nesta máquina. Informacional: não bloqueia nada."""
    if not achados:
        return "\nPré-requisitos: tudo certo para os clientes detectados.\n"
    partes = ["\nPré-requisitos desta máquina:\n\n"]
    for a in achados:
        partes.append(_bloco_achado(a, arquitetura))
        partes.append("\n")
    return "".join(partes)


def _bloco_achado(achado, arquitetura) -> str:
    if achado.codigo == "sem_shell":
        return (
            f"  ! {achado.cliente}: não vai conseguir executar comandos aqui.\n"
            "    A sessão abre normalmente e o contexto chega — o agente lê e\n"
            "    escreve arquivos. O que não funciona é rodar comando: este\n"
            "    cliente usa PowerShell e só PowerShell, e a política desta\n"
            "    máquina o bloqueia.\n"
            "    Não há ajuste no Koine nem no cliente, e instalar o Git Bash\n"
            "    NÃO resolve para ele. O caminho é pedir liberação à TI.\n")
    if achado.codigo == "claude_sem_bash":
        arquivo = _ARQUIVO_GIT.get((arquitetura or "").upper(),
                                   "Git for Windows Setup da sua arquitetura")
        return (
            "  ! claude: precisa do Git Bash nesta máquina.\n"
            "    A política bloqueia o PowerShell, e o Claude Code usa\n"
            "    PowerShell ou bash. Instale o Git para Windows:\n"
            "      https://git-scm.com/download/win\n"
            f"      arquivo: {arquivo}\n"
            "    Não precisa de administrador, e deixe o local padrão que o\n"
            "    instalador sugere — o Claude procura a instalação do Git nesse\n"
            "    lugar, não no PATH. Depois disso não há mais nenhum passo.\n")
    if achado.codigo == "opencode_tui_arm64":
        return (
            "  ! opencode: a interface de terminal não abre em Windows ARM64.\n"
            "    É bug do próprio OpenCode, não do Koine nem desta máquina.\n"
            "    Alternativa enquanto não sai correção: `opencode web`.\n")
    if achado.codigo == "codex_incompleto":
        return (
            "  ! codex: a instalação está incompleta e toda ferramenta vai\n"
            "    falhar — falta o `codex-code-mode-host` ao lado do binário.\n"
            "    Reinstale pelo pacote completo (`codex-package-<arch>`), não\n"
            "    pelo zip do executável isolado.\n")
    return f"  ! {achado.cliente}: {achado.codigo}\n"


def aviso_launch_sem_shell(cliente: str, codigo: str = "sem_shell") -> str:
    """Uma linha, no stderr, antes do cliente subir.

    Avisa e não bloqueia: a sessão tem valor sem shell — o contexto chega e o
    agente lê e escreve arquivos. Recusar a abrir tiraria do usuário mais do que
    a política tirou. Mesma limitação do aviso de ficha reposta: vai para o
    stderr antes do `execvpe`, e em sessão remota pode não chegar.

    Duas formas, porque um dos casos tem saída e o outro não.
    """
    if codigo == "claude_sem_bash":
        return (f"aviso: {cliente} não consegue executar comandos nesta máquina "
                "— instale o Git Bash (https://git-scm.com/download/win, sem "
                "administrador). A sessão abre assim mesmo.")
    return (f"aviso: {cliente} não consegue executar comandos nesta máquina "
            "(PowerShell bloqueado por política) — a sessão abre, mas sem shell.")


def path_resultado(status, pasta, na_sessao) -> str:
    """O que dizer depois de mexer (ou não) no PATH do usuário.

    Três situações distintas, que o aviso antigo colapsava numa mentira só: ele
    comparava contra a SESSÃO e dizia "não está no seu PATH" com a pasta já no
    registro.
    """
    if status == "adicionado":
        return (f"\n✓ {pasta} acrescentado ao PATH do seu usuário.\n"
                "  Reabra o terminal para os comandos `koine` e `kn-*` funcionarem\n"
                "  pelo nome.\n")
    if status == "ja_estava":
        if na_sessao:
            return ""
        return (f"\n{pasta} já está no PATH do seu usuário, mas não neste terminal —\n"
                "  ele foi aberto antes. Reabra o terminal e os comandos `koine` e\n"
                "  `kn-*` funcionarão pelo nome.\n")
    return (f"\n! não consegui acrescentar {pasta} ao PATH do seu usuário.\n"
            "  Sem isso, os comandos só funcionam pelo caminho completo.\n"
            "  Para fazer à mão, sem administrador:\n"
            "    1. rode:  rundll32 sysdm.cpl,EditEnvironmentVariables\n"
            "    2. em Variáveis de usuário, selecione Path e clique em Editar\n"
            f"    3. Novo  →  {pasta}  →  OK\n"
            "    4. reabra o terminal\n")
