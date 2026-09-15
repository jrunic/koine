"""Diagnóstico do Paseo — leitura pura (jd-task #879).

NENHUMA função deste módulo escreve, reinicia ou consome credencial. Quem
escreve config é o `paseo-configurar`; quem escreve provider é o
`paseo-provider`. Diagnóstico que também conserta vira duas superfícies para
manter e uma para desconfiar.

As medições que definiram cada decisão estão nos documentos internos do autor,
fora deste repositório; as que importam para ler o código estão repetidas nos
docstrings de cada verificação, com a data. Todas são de 13/09/2026, contra o
Paseo 0.8.0.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

OK = "ok"
AVISO = "aviso"
ERRO = "erro"

# Sentinela para o tristate das chaves. `None` não serve: `null` é valor
# legítimo de JSON, e confundir "ausente" com "presente e nulo" é exatamente a
# distinção que o critério 3 da spec exige preservar.
AUSENTE = object()


@dataclass(frozen=True)
class Verificacao:
    """Resultado de UMA verificação.

    `id` é o contrato com quem consome o `--json` — estável, nunca traduzido.
    `mensagem` é para humano e pode mudar sem quebrar ninguém.
    """
    id: str
    situacao: str
    mensagem: str
    dado: dict = field(default_factory=dict)


def home_do_paseo() -> str:
    """Diretório de estado do Paseo.

    Medido em 13/09/2026: a CLI do Paseo honra `PASEO_HOME` e expõe `--home`,
    com default `~/.paseo`. Respeitar a variável é o que torna esta suíte
    executável sem tocar na máquina de quem roda o teste.
    """
    return os.environ.get("PASEO_HOME") or os.path.join(
        os.path.expanduser("~"), ".paseo")


def ler_config(home: str) -> tuple[dict | None, Verificacao]:
    """Lê o config do Paseo. Devolve (config, verificação).

    Config ilegível encerra o diagnóstico: sem ele, toda verificação seguinte
    mediria a ausência do arquivo e não o que se quer saber — nove erros
    dizendo a mesma coisa, que é ruído com aparência de rigor.
    """
    caminho = os.path.join(home, "config.json")
    if not os.path.isfile(caminho):
        return None, Verificacao(
            "config.legivel", ERRO,
            f"não há config do Paseo em {caminho}. "
            "Rode `koine paseo-configurar` para criá-lo.",
            {"motivo": "ausente", "caminho": caminho})
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f), Verificacao(
                "config.legivel", OK, f"config lido de {caminho}.",
                {"caminho": caminho})
    except (json.JSONDecodeError, OSError) as e:
        return None, Verificacao(
            "config.legivel", ERRO,
            f"o config em {caminho} não pôde ser lido: {e}. "
            "O Paseo não sobe com config inválido — abra o arquivo antes de "
            "qualquer outra coisa.",
            {"motivo": "invalido", "caminho": caminho, "erro": str(e)})


def busca(cfg: dict, caminho: str):
    """Valor de uma chave pontilhada, ou AUSENTE.

    Devolve a sentinela em vez de None porque `null` é valor legítimo de JSON:
    colapsar os dois apagaria a distinção que o comando existe para fazer.
    """
    atual = cfg
    for parte in caminho.split("."):
        if not isinstance(atual, dict) or parte not in atual:
            return AUSENTE
        atual = atual[parte]
    return atual


def verificar_chave_do_canal(cfg: dict, caminho: str) -> Verificacao:
    """Chave cuja ausência OU desligamento tira capacidade sem avisar.

    São `daemon.browserTools.enabled` e `daemon.mcp.injectIntoAgents`. Medido em
    13/09/2026: as duas têm zero ocorrências no repo — nem a prosa nem o código
    as conheciam —, e foi uma delas que deixou uma usuária dias sem o navegador.
    """
    valor = busca(cfg, caminho)
    ident = f"config.{caminho}"
    if valor is AUSENTE:
        return Verificacao(
            ident, ERRO,
            f"a chave `{caminho}` não existe no config. "
            "Rode `koine paseo-configurar` para escrevê-la.",
            {"estado": "ausente", "chave": caminho})
    if valor is not True:
        return Verificacao(
            ident, ERRO,
            f"a chave `{caminho}` está desligada. A capacidade some sem "
            "mensagem de erro — foi assim que uma instalação ficou dias sem o "
            "navegador interno. Rode `koine paseo-configurar`.",
            {"estado": "desligada", "chave": caminho, "valor": valor})
    return Verificacao(ident, OK, f"`{caminho}` ligada.",
                       {"estado": "ligada", "chave": caminho})


def verificar_relay(cfg: dict) -> Verificacao:
    """O relay é decisão do usuário; a AUSÊNCIA da chave é que é defeito.

    Medido em 30/08/2026, contra o que a documentação afirma: com a chave de
    relay ausente o serviço conecta assim mesmo e EXPÕE a máquina. Ligado ou
    desligado é escolha, e a /kn-04 é quem a conduz com o usuário.
    """
    valor = busca(cfg, "daemon.relay.enabled")
    if valor is AUSENTE:
        return Verificacao(
            "config.daemon.relay.enabled", ERRO,
            "a chave `daemon.relay.enabled` não existe no config. Sem ela o "
            "serviço conecta assim mesmo e expõe esta máquina — não é o mesmo "
            "que estar desligada. Rode `koine paseo-configurar`.",
            {"estado": "ausente"})
    return Verificacao(
        "config.daemon.relay.enabled", OK,
        "relay ligado — esta máquina é alcançável pelo serviço de relay."
        if valor else
        "relay desligado — esta máquina só é alcançável pela sua própria rede.",
        {"estado": "declarada", "habilitado": bool(valor)})


def verificar_voz(cfg: dict) -> Verificacao:
    """Ditado e fala configurados?

    Aviso e nunca erro: a máquina funciona sem voz. O caminho da chave é o
    medido em 13/09/2026 contra o Paseo 0.8.0 — se uma versão futura mudá-lo, o
    desfecho é um aviso a mais, nunca uma reprovação indevida, que é a
    assimetria certa para um sinal opcional.
    """
    provedor = busca(cfg, "daemon.voice.sttProvider")
    if provedor is AUSENTE:
        return Verificacao(
            "config.voz", AVISO,
            "o ditado não está configurado. Se você quiser falar em vez de "
            "digitar, a `/kn-04-conecta-o-paseo` configura.",
            {"provedor": None})
    return Verificacao("config.voz", OK,
                       f"ditado configurado com `{provedor}`.",
                       {"provedor": provedor})


def _rodar_paseo(args: list[str], *, timeout: int = 15) -> str | None:
    """Única porta de saída para a CLI do Paseo. Devolve stdout ou None.

    Resolve o executável pelo ambiente (PATH → local padrão de instalação)
    e executa pela primitiva certa do SO (`cmd /c` para `.cmd`/`.bat` no
    Windows). None significa "não deu para perguntar" — sem executável,
    estouro de prazo ou saída não-zero. Quem chama decide o que isso quer
    dizer no contexto dele; este módulo não transforma silêncio em veredito.
    """
    from koine import paseo_ambiente
    exe = paseo_ambiente.resolver_executavel("paseo")
    if exe is None:
        return None
    try:
        r = paseo_ambiente.executar(exe.caminho, args, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError):
        return None
    return r.stdout if r.returncode == 0 else None


def verificar_executaveis() -> Verificacao:
    """`paseo` alcançável? Fora do PATH vira aviso com o diretório exato a
    inserir — o mentorado copia e cola, não adivinha (spec 20260915)."""
    from koine import paseo_ambiente as amb
    exe = amb.resolver_executavel("paseo")
    if exe is None:
        procurados = amb.pastas_padrao_do_paseo()
        return Verificacao(
            "executaveis.paseo", ERRO,
            "não encontrei o comando `paseo` — nem no PATH, nem em "
            + (", ".join(procurados) if procurados else "local padrão nenhum")
            + ". Reinstale o aplicativo Paseo.",
            {"estado": "ausente", "procurados": procurados})
    if exe.origem == "fallback":
        pasta = os.path.dirname(exe.caminho)
        return Verificacao(
            "executaveis.paseo", AVISO,
            f"o comando do Paseo está em {exe.caminho}, mas essa pasta não "
            f"está no seu PATH. Para chamar `paseo` de qualquer terminal, "
            f"adicione ao PATH: {pasta}",
            {"estado": "fora-do-path", "caminho": exe.caminho, "pasta": pasta})
    return Verificacao("executaveis.paseo", OK,
                       "comando `paseo` alcançável pelo PATH.",
                       {"estado": "no-path", "caminho": exe.caminho})


def campo_do_status(saida: str, rotulo: str) -> str | None:
    """Valor de um campo da tabela do `paseo status`."""
    for linha in saida.splitlines():
        if linha.startswith(rotulo):
            valor = linha[len(rotulo):].strip()
            return valor or None
    return None


def verificar_servico(cfg: dict) -> Verificacao:
    """O serviço está de pé e escutando onde o config manda?"""
    declarado = busca(cfg, "daemon.listen")
    declarado = None if declarado is AUSENTE else declarado
    saida = _rodar_paseo(["status"])
    if saida is None:
        return Verificacao(
            "servico.escutando", ERRO,
            "não foi possível falar com o serviço do Paseo. Ou ele está fora "
            "do ar, ou o comando `paseo` não está no seu PATH. Abra o "
            "aplicativo Paseo e tente de novo.",
            {"motivo": "cli-ausente", "listen_declarado": declarado})
    ouvindo = campo_do_status(saida, "Listen")
    if ouvindo is None:
        return Verificacao(
            "servico.escutando", ERRO,
            "o serviço respondeu mas não disse em que endereço escuta.",
            {"motivo": "sem-listen", "listen_declarado": declarado})
    return Verificacao(
        "servico.escutando", OK,
        f"serviço de pé, escutando em {ouvindo}.",
        {"listen": ouvindo, "listen_declarado": declarado})


def verificar_versoes() -> Verificacao:
    """O aplicativo e o serviço estão na mesma versão?"""
    bruto = _rodar_paseo(["--version"])
    app = bruto.strip() if bruto else None
    status = _rodar_paseo(["status"])
    daemon = campo_do_status(status, "Daemon Version") if status else None

    if app is None:
        return Verificacao("versao.aplicativo_e_daemon", ERRO,
                           "não foi possível ler a versão do Paseo.",
                           {"aplicativo": None, "daemon": daemon})
    if daemon is None:
        return Verificacao(
            "versao.aplicativo_e_daemon", AVISO,
            f"aplicativo na {app}; esta versão não publica a do serviço, "
            "então não dá para comparar as duas.",
            {"aplicativo": app, "daemon": None})
    if app != daemon:
        return Verificacao(
            "versao.aplicativo_e_daemon", ERRO,
            f"o aplicativo está na {app} e o serviço na {daemon}. Quem atende "
            "as suas sessões é o serviço. Feche o Paseo e abra de novo; "
            "persistindo, reinstale o aplicativo.",
            {"aplicativo": app, "daemon": daemon})
    return Verificacao("versao.aplicativo_e_daemon", OK,
                       f"aplicativo e serviço na {app}.",
                       {"aplicativo": app, "daemon": daemon})


def _criado_em(caminho: str) -> str:
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f).get("createdAt") or ""
    except (json.JSONDecodeError, OSError):
        return ""


def _tem_mcp(caminho: str) -> bool:
    try:
        with open(caminho, encoding="utf-8") as f:
            d = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False
    return bool(((d.get("persistence") or {}).get("metadata") or {})
                .get("mcpServers"))


def verificar_mcp_nos_agentes(cfg: dict, home: str) -> Verificacao:
    """As sessões criadas DEPOIS que a injeção começou receberam o MCP?"""
    if busca(cfg, "daemon.mcp.injectIntoAgents") is not True:
        return Verificacao(
            "agentes.mcp_injetado", OK,
            "injeção do MCP desligada no config — nada a conferir aqui.",
            {"estado": "desligada", "sem_mcp": 0})

    arquivos = glob.glob(os.path.join(home, "agents", "*", "*.json"))
    if not arquivos:
        return Verificacao(
            "agentes.mcp_injetado", OK,
            "ainda não há sessões nesta máquina — nada a conferir.",
            {"estado": "sem-agentes", "sem_mcp": 0})

    com_mcp = [a for a in arquivos if _tem_mcp(a)]
    sem_mcp = [a for a in arquivos if a not in com_mcp]

    if not com_mcp:
        return Verificacao(
            "agentes.mcp_injetado", AVISO,
            "a injeção do MCP está ligada e nenhuma sessão desta máquina a "
            "recebeu. Se você acabou de ligá-la, abra uma sessão nova e rode "
            "este comando de novo: é isso que diz se ela está funcionando.",
            {"estado": "sem-fronteira", "sem_mcp": len(sem_mcp),
             "anteriores_a_fronteira": 0})

    fronteira = min(_criado_em(a) for a in com_mcp)
    posteriores = [a for a in sem_mcp if _criado_em(a) > fronteira]
    anteriores = len(sem_mcp) - len(posteriores)

    if posteriores:
        return Verificacao(
            "agentes.mcp_injetado", ERRO,
            f"{len(posteriores)} sessão(ões) criada(s) depois que a injeção do "
            "MCP começou a funcionar não a receberam, embora o config mande "
            "injetar. Feche o Paseo e abra de novo; persistindo, é defeito "
            "para relatar.",
            {"estado": "quebrado", "sem_mcp": len(posteriores),
             "anteriores_a_fronteira": anteriores, "fronteira": fronteira,
             "exemplos": [os.path.basename(a) for a in posteriores[:3]]})

    msg = "todas as sessões criadas desde que a injeção começou receberam o MCP."
    if anteriores:
        msg += (f" ({anteriores} sessão(ões) mais antiga(s) não têm, e é "
                "esperado: foram criadas antes de a chave ser ligada.)")
    return Verificacao(
        "agentes.mcp_injetado", OK, msg,
        {"estado": "ok", "sem_mcp": 0, "anteriores_a_fronteira": anteriores,
         "fronteira": fronteira})


COOKIES_VAZIO = 20480


def particoes_do_navegador() -> str | None:
    """Onde o navegador interno guarda o estado das sessões. None se não medido."""
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library",
                            "Application Support", "Paseo", "Partitions")
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        return os.path.join(appdata, "Paseo", "Partitions") if appdata else None
    return None


def verificar_navegador(cfg: dict, base_particoes: str) -> Verificacao:
    """O navegador interno está ligado, e já foi usado para login?"""
    chave = busca(cfg, "daemon.browserTools.enabled")
    if chave is not True:
        return Verificacao(
            "navegador.interno", ERRO,
            "o navegador interno está desligado no config — por isso ele "
            "responde que não está logado. Rode `koine paseo-configurar`.",
            {"habilitado": False, "tem_sessao": None, "estado": "desligado"})

    cookies = (os.path.join(base_particoes, "paseo-browser", "Cookies")
               if base_particoes else None)
    if cookies is None or not os.path.isfile(cookies):
        return Verificacao(
            "navegador.interno", AVISO,
            "o navegador interno está ligado. Não consegui conferir se ele já "
            "foi usado para entrar em algum site nesta plataforma — se o agente "
            "responder `Please run login`, entre uma vez dentro dele e as "
            "próximas sessões aproveitam.",
            {"habilitado": True, "tem_sessao": None, "estado": "nao-medido",
             "base": base_particoes})

    tamanho = os.path.getsize(cookies)
    if tamanho <= COOKIES_VAZIO:
        return Verificacao(
            "navegador.interno", AVISO,
            "o navegador interno está ligado e nunca foi usado para entrar em "
            "nenhum site. Se o agente responder `Please run login`, é isto: "
            "entre uma vez dentro dele e as próximas sessões aproveitam.",
            {"habilitado": True, "tem_sessao": False, "estado": "sem-login",
             "bytes": tamanho})
    return Verificacao(
        "navegador.interno", OK,
        "navegador interno ligado, com sessão gravada. (Se um site específico "
        "pedir login, é daquele site — entre nele uma vez.)",
        {"habilitado": True, "tem_sessao": True, "estado": "com-login",
         "bytes": tamanho})


def _prescritos() -> list[str]:
    from koine import paseo as _p
    nomes = []
    for cliente in _p.com_rota():
        nomes.append(_p.entry_de(cliente))
        nomes.append(_p.entry_hermes_de(cliente))
    return nomes


def _disponiveis() -> set[str] | None:
    saida = _rodar_paseo(["provider", "ls", "--json"])
    if saida is None:
        return None
    try:
        lista = json.loads(saida)
    except json.JSONDecodeError:
        return None
    return {p.get("provider") for p in lista if p.get("status") == "available"}


def verificar_providers(cfg: dict) -> Verificacao:
    """Os providers que o Koine prescreve estão no config?"""
    declarados = busca(cfg, "agents.providers")
    declarados = {} if declarados is AUSENTE else declarados
    prescritos = _prescritos()
    presentes = [n for n in prescritos if n in declarados]
    faltando = [n for n in prescritos if n not in declarados]

    if not presentes:
        return Verificacao(
            "providers.do_koine", OK,
            "esta máquina ainda não tem os agentes do Koine no Paseo. "
            "Rode `/kn-04-conecta-o-paseo` para configurá-los.",
            {"estado": "nao-adotado", "presentes": [], "faltando": faltando,
             "indisponiveis": []})
    if faltando:
        return Verificacao(
            "providers.do_koine", ERRO,
            f"{len(presentes)} de {len(prescritos)} agentes do Koine estão "
            f"configurados; faltam {', '.join(faltando)}. A sessão aberta por "
            "um que falta sobe sem o seu contexto e sem erro. "
            "Rode `/kn-04-conecta-o-paseo`.",
            {"estado": "parcial", "presentes": presentes, "faltando": faltando,
             "indisponiveis": []})

    vistos = _disponiveis()
    if vistos is not None:
        mortos = [n for n in presentes if n not in vistos]
        if mortos:
            return Verificacao(
                "providers.do_koine", ERRO,
                f"{', '.join(mortos)} está(ão) no config e o serviço não "
                "consegue usá-lo(s) — a sessão aparece na lista e não sobe. "
                "Se você acabou de reiniciar o Paseo, espere alguns segundos e "
                "rode de novo; persistindo, rode `/kn-04-conecta-o-paseo`.",
                {"estado": "indisponivel", "presentes": presentes,
                 "faltando": [], "indisponiveis": mortos})

    return Verificacao(
        "providers.do_koine", OK,
        f"os {len(prescritos)} agentes do Koine estão configurados.",
        {"estado": "completo", "presentes": presentes, "faltando": [],
         "indisponiveis": []})


CHAVES_DO_CANAL = ("daemon.browserTools.enabled", "daemon.mcp.injectIntoAgents")


def diagnosticar(home: str | None = None) -> list[Verificacao]:
    """Roda todas as verificações, na ordem em que serão lidas."""
    home = home or home_do_paseo()
    cfg, v_config = ler_config(home)
    if cfg is None:
        return [v_config]

    fora = [v_config, verificar_executaveis(), verificar_servico(cfg),
            verificar_versoes()]
    for chave in CHAVES_DO_CANAL:
        fora.append(verificar_chave_do_canal(cfg, chave))
    fora.append(verificar_relay(cfg))
    fora.append(verificar_voz(cfg))
    fora.append(verificar_mcp_nos_agentes(cfg, home))
    fora.append(verificar_navegador(cfg, particoes_do_navegador()))
    fora.append(verificar_providers(cfg))
    return fora


def codigo_de_saida(verificacoes: list[Verificacao]) -> int:
    """Só `erro` reprova. Aviso é informação, e informação não barra ninguém."""
    return 1 if any(v.situacao == ERRO for v in verificacoes) else 0
