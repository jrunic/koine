"""Leitura do frontmatter da Ficha Koine — tolerante ao YAML que gente escreve.

Quem escreve esses arquivos é um usuário comum descrevendo o próprio trabalho em
português, à mão ou pela boca de um agente. `descricao: Vendas B2B: acompanhamento e metas` é a forma natural de escrever e é YAML inválido. Antes da correção
isso derrubava o Koine inteiro com um ScannerError de 20 linhas.

Política: parse estrito primeiro; só quando ele falha, tenta reparar as linhas
`chave: valor` que sozinhas não parseiam, recitando o valor. O reparo nunca roda
sobre arquivo que já é válido. O que sobra de irreparável vira `FrontmatterInvalido`
com arquivo/linha/coluna — a lib devolve o erro nomeado, o consumidor decide a
política (degradar, pular o arquivo, abortar).
"""

import os
import re
import sys
from dataclasses import dataclass

from koine._vendor import yaml

# `chave: valor` no topo do bloco (sem indentação). Item de lista, linha
# indentada e continuação de bloco escalar não casam — e não devem mesmo.
_CHAVE = re.compile(r"^([A-Za-z_][\w.-]*):[ \t]+(\S.*?)[ \t]*$")

# Valor que começa com um destes é estrutura YAML (lista, mapa, bloco, âncora,
# tag), não texto solto do usuário: recitar corromperia o dado.
_ESTRUTURA = "[{|>&*!%@`"

# Paths já avisados neste processo — o launch relê o mesmo CONTEXTO.md três
# vezes (classificar → _montar_cm → resolver) e um aviso basta.
_avisados: set[str] = set()


class FrontmatterInvalido(Exception):
    """Frontmatter que nem o reparo salva, ou que não é um mapa `chave: valor`."""

    def __init__(self, motivo: str, arquivo: str | None = None,
                 linha: int | None = None, coluna: int | None = None):
        self.motivo = motivo
        self.arquivo = arquivo
        self.linha = linha
        self.coluna = coluna
        super().__init__(str(self))

    def __str__(self) -> str:
        onde = self.arquivo or "frontmatter"
        if self.linha:
            onde += f", linha {self.linha}"
            if self.coluna:
                onde += f", coluna {self.coluna}"
        return f"{onde}: {self.motivo}"

    def com_arquivo(self, arquivo: str) -> "FrontmatterInvalido":
        """Mesma falha, agora sabendo de qual arquivo veio."""
        return FrontmatterInvalido(self.motivo, arquivo, self.linha, self.coluna)


def ler(texto: str) -> tuple[dict, str]:
    """Devolve (frontmatter_dict, corpo). Sem frontmatter → ({}, texto).
    Levanta FrontmatterInvalido se o YAML for irreparável ou não for um mapa."""
    fm, _, corpo = analisar(texto)
    return fm, corpo


@dataclass
class _Fatia:
    """Onde o bloco de frontmatter começa e termina no texto original. Índices,
    não cópias: é o que permite recompor o arquivo preservando tudo que está
    fora do bloco."""
    inicio: int
    fim: int
    bloco: str
    corpo: str


def _fatiar(texto: str) -> "_Fatia | None":
    """None quando não há frontmatter delimitado."""
    if not texto.startswith("---"):
        return None
    # separa o bloco --- ... --- inicial do corpo
    partes = texto.split("\n", 1)
    if len(partes) == 1:
        return None
    inicio = len(partes[0]) + 1
    resto = partes[1]
    fim_rel = resto.find("\n---")
    if fim_rel == -1:
        return None
    bloco = resto[:fim_rel]
    corpo = resto[fim_rel + len("\n---"):].lstrip("\n")
    return _Fatia(inicio, inicio + len(bloco), bloco, corpo)


def analisar(texto: str) -> tuple[dict, list[str], str]:
    """Como `ler`, mas devolve também as chaves que precisaram de reparo — é o
    que permite ao `koine validar` distinguir 'válido' de 'passou no tapa'."""
    fatia = _fatiar(texto)
    if fatia is None:
        return {}, [], texto
    dados, reparos = _carregar(fatia.bloco)
    return dados, reparos, fatia.corpo


def ler_arquivo(path: str, normalizar_disco: bool = False) -> tuple[dict, str]:
    """`ler` a partir do caminho: erros nomeiam o arquivo e o reparo avisa uma
    vez por arquivo no stderr — tolerar dado ruim não é escondê-lo.

    `normalizar_disco=True` conserta o arquivo de fato. Desligado por padrão:
    leitura não escreve por tabela, e quem varre a base de conhecimento do
    usuário (o walker do índice) não deve reescrevê-la sozinho."""
    if normalizar_disco:
        from koine import ficha  # tardio: ficha importa frontmatter
        ficha.normalizar_arquivo(path)
    with open(path, encoding="utf-8") as f:
        texto = f.read()
    try:
        fm, reparos, corpo = analisar(texto)
    except FrontmatterInvalido as e:
        raise e.com_arquivo(path) from None
    if reparos:
        _avisar(path, reparos)
    return fm, corpo


def normalizar(texto: str) -> tuple[str, list[str]]:
    """Texto com o frontmatter consertado no lugar, e as chaves corrigidas.
    Nada a fazer — válido, sem frontmatter, irreparável — devolve o texto
    original e lista vazia. Nunca uma versão pior dele.

    Diff mínimo é requisito, não elegância: só as linhas citadas mudam, cada
    uma com o terminador que já tinha. É o que torna aceitável reescrever o
    arquivo do usuário sem perguntar."""
    fatia = _fatiar(texto)
    if fatia is None:
        return texto, []
    decisoes = _decidir(fatia.bloco.splitlines())
    if not decisoes:
        return texto, []
    linhas = fatia.bloco.splitlines(keepends=True)
    for i, _, nova in decisoes:
        fim_de_linha = linhas[i][len(linhas[i].rstrip("\r\n")):]
        linhas[i] = nova + fim_de_linha
    candidato = texto[:fatia.inicio] + "".join(linhas) + texto[fatia.fim:]
    # o bloco reparado parseia, mas o documento remendado é outra string:
    # confere antes de devolver, para não haver caminho onde a correção
    # automática grave algo pior que o original
    try:
        _, reparos, _ = analisar(candidato)
    except FrontmatterInvalido:
        return texto, []
    if reparos:
        return texto, []
    return candidato, [chave for _, chave, _ in decisoes]


def silenciar_aviso(path: str) -> None:
    """Marca `path` como já avisado. Quem chama é o `ficha`, quando já reportou
    algo mais preciso sobre o mesmo arquivo — dois subsistemas avisando sobre o
    mesmo frontmatter é ruído, e o mais específico ganha."""
    _avisados.add(os.path.abspath(path))


def _avisar(path: str, reparos: list[str]) -> None:
    if os.path.abspath(path) in _avisados:
        return
    _avisados.add(os.path.abspath(path))
    campos = ", ".join(f"`{c}`" for c in reparos)
    print(f"aviso: em {path}, o valor de {campos} tem `:` sem aspas — o Koine "
          f"leu assim mesmo. Para silenciar, cite o valor entre aspas duplas "
          f"(ex.: {reparos[0]}: \"texto: com dois-pontos\").", file=sys.stderr)


def _carregar(bloco: str) -> tuple[dict, list[str]]:
    try:
        return _mapa(yaml.safe_load(bloco)), []
    except yaml.YAMLError as e:
        erro = e  # `as e` some ao sair do except; o mark é preciso no original
    reparado, reparos = _reparar(bloco)
    if reparos:
        try:
            return _mapa(yaml.safe_load(reparado)), reparos
        except yaml.YAMLError:
            pass
    raise _invalido(erro)


def _mapa(dados) -> dict:
    """Bloco vazio → {}. Escalar ou lista no lugar do mapa é frontmatter
    inválido: sem isso, `fm.get(...)` estoura AttributeError no consumidor."""
    if dados is None:
        return {}
    if not isinstance(dados, dict):
        raise FrontmatterInvalido(
            f"o frontmatter precisa ser uma lista de `chave: valor` "
            f"(li um {type(dados).__name__})")
    return dados


def _citar(valor: str) -> str:
    """Aspas duplas por padrão — é o que a documentação e os templates das
    skills recomendam, e o Koine não pode contradizer a própria orientação.
    Simples quando o valor tem `"` ou `\\`: caminho do Windows
    (`C:\\Users\\usuario`) entre aspas duplas vira escape inválido, e quem escreve
    caminho do Windows é justamente o usuário-alvo."""
    if '"' in valor or "\\" in valor:
        return "'" + valor.replace("'", "''") + "'"
    return '"' + valor + '"'


def compor(fm: dict) -> str:
    """Bloco de frontmatter a partir de um mapa, com os valores citados quando
    precisam. Emissão própria em vez de `yaml.dump` para manter a ordem das
    chaves e o estilo do resto do repositório.

    É o que impede o Koine de gravar YAML inválido em arquivo que ele mesmo
    gera: o nome de um domínio vem da lista do usuário e pode conter `:`."""
    linhas = ["---"]
    for chave, valor in fm.items():
        if isinstance(valor, int) and not isinstance(valor, bool):
            linhas.append(f"{chave}: {valor}")
            continue
        texto = str(valor)
        # cita quando o round-trip não devolve exatamente a mesma string —
        # pega tanto `a: b: c` (não parseia) quanto `status: yes` (viraria bool)
        cru = f"{chave}: {texto}"
        try:
            fiel = yaml.safe_load(cru) == {chave: texto}
        except yaml.YAMLError:
            fiel = False
        linhas.append(cru if fiel else f"{chave}: {_citar(texto)}")
    linhas.append("---")
    return "\n".join(linhas)


def _decidir(linhas: list[str]) -> list[tuple[int, str, str]]:
    """Quais linhas precisam de reparo e como ficariam: (índice, chave, linha).
    Recita o valor das linhas `chave: valor` que sozinhas não parseiam — a
    linha é testada isolada, então uma linha já válida no mesmo bloco
    (`descricao: "Vendas: meta"`) atravessa intacta.

    Só decide, não junta. A junção é de quem chama, porque o parser quer um
    bloco achatado e o arquivo em disco quer o terminador original de cada
    linha preservado."""
    decisoes = []
    for i, linha in enumerate(linhas):
        m = _CHAVE.match(linha)
        if not m or _parseia(linha):
            continue
        chave, valor = m.group(1), m.group(2)
        if valor[0] in _ESTRUTURA:
            continue
        decisoes.append((i, chave, f"{chave}: {_citar(valor)}"))
    return decisoes


def _reparar(bloco: str) -> tuple[str, list[str]]:
    """Bloco reparado para o parser. Achatado em `\\n` de propósito: é efêmero,
    só alimenta o safe_load. Para reescrever o arquivo do usuário existe
    `normalizar`, que preserva o terminador de cada linha — em arquivo CRLF
    (Windows, onde o bug foi visto) juntar com `\\n` engoliria os `\\r`."""
    linhas = bloco.splitlines()
    decisoes = _decidir(linhas)
    for i, _, nova in decisoes:
        linhas[i] = nova
    return "\n".join(linhas), [chave for _, chave, _ in decisoes]


def _parseia(linha: str) -> bool:
    try:
        return isinstance(yaml.safe_load(linha), dict)
    except yaml.YAMLError:
        return False


def _invalido(erro: yaml.YAMLError) -> FrontmatterInvalido:
    motivo = getattr(erro, "problem", None) or "YAML inválido"
    marca = getattr(erro, "problem_mark", None)
    if marca is None:
        return FrontmatterInvalido(motivo)
    # o bloco começa na 2ª linha do arquivo (a 1ª é o `---`); mark é 0-based
    return FrontmatterInvalido(motivo, linha=marca.line + 2, coluna=marca.column + 1)


def definir_campo(texto: str, chave: str, valor: str) -> tuple[str, bool]:
    """Texto com `chave: valor` no frontmatter, e se houve mudança.

    Edita UMA linha e recompõe pelos índices de `_fatiar` — mesma disciplina do
    `normalizar`: diff mínimo é requisito. Recompor o bloco a partir do dict
    apagaria comentário e ordem do usuário.

    Sem bloco de frontmatter, não escreve: arquivo assim é pasta INCOMPLETA, e
    criar a ficha aqui seria o Koine inventando estado que ele decidiu não
    inventar (v0.6.1).
    """
    fatia = _fatiar(texto)
    if fatia is None:
        return texto, False

    linhas = fatia.bloco.splitlines(keepends=True)
    prefixo = f"{chave}:"
    for i, linha in enumerate(linhas):
        if not linha.startswith(prefixo):
            continue
        if linha.rstrip("\r\n").strip() == f"{chave}: {valor}":
            return texto, False                       # no-op: mesmo valor
        fim = linha[len(linha.rstrip("\r\n")):]
        linhas[i] = f"{chave}: {valor}{fim}"
        break
    else:
        # `_fatiar` recorta o bloco SEM os delimitadores, cortando em `\n---`:
        # a última linha vem sem terminador, e por isso o terminador da linha
        # nova vai ANTES dela — depois, o campo colaria na linha anterior.
        #
        # Num arquivo CRLF há uma segunda ponta: o `\n` do corte pertence ao
        # `\r\n` da última linha, então o bloco termina com um `\r` pendurado.
        # Acrescentar depois dele produz `\r\r\n`. A linha nova entra ANTES do
        # `\r`, que volta ao fim. Achado pelo teste de CRLF, não no papel.
        crlf = "\r\n" in fatia.bloco or fatia.bloco.endswith("\r")
        term = "\r\n" if crlf else "\n"
        cauda = ""
        if fatia.bloco.endswith("\r"):
            linhas[-1] = linhas[-1][:-1]
            cauda = "\r"
        linhas.append(f"{term}{chave}: {valor}{cauda}")

    return texto[:fatia.inicio] + "".join(linhas) + texto[fatia.fim:], True
