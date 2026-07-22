---
descricao: Guia de instalação do Koine v0.4.x — macOS, Linux e Windows; upgrade da v0.3.x (Go); passo a passo manual com explicação de cada comando (o que os installers automatizam); variantes, verificação e solução de problemas
id: 202607090130
tipo: guia
status: ativo
tags: [guia, instalacao, upgrade, windows, macos, linux]
---

# Guia — Instalar o Koine

Audiência: quem vai instalar o Koine numa máquina própria ou corporativa. Assume terminal básico e um cliente IA de terminal já em uso (ou a instalar depois — o installer orienta).

Para a primeira sessão após instalar, siga o tutorial [Onboarding completo](../tutoriais/onboarding-completo.md). Para a lista de comandos, veja a [referência da CLI](../referencias/cli.md).

## Pré-requisito: Python 3.12 ou superior

O Koine é distribuído como aplicação Python (`koine.pyz`) — sem executável compilado. Verifique:

```bash
python3 --version    # macOS/Linux
py -3 --version      # Windows
```

Se não houver Python ≥ 3.12:

- **macOS:** `brew install python` (ou <https://www.python.org/downloads/>). Atenção: o `python3` que vem com o macOS é 3.9 — o installer procura versões novas primeiro e ignora o antigo, mas o pré-requisito continua seu.
- **Windows:** instalador oficial em <https://www.python.org/downloads/> — ou o Python homologado pela sua TI (ambiente corporativo).
- **Linux:** gerenciador do sistema (`apt install python3`, `dnf install python3` etc.).

## macOS e Linux

```bash
curl -fsSL https://github.com/jrunic/koine/releases/latest/download/install.sh | sh
```

O script localiza o interpretador, baixa o pacote da release, extrai em `~/.local/share/koine/dist/` e conclui a instalação (vault, wrappers `koine` e `kn-*` em `~/.local/bin/`, pasta canônica `~/koine`). Num terminal interativo ele pergunta a pasta canônica e oferece instalar as skills dos clientes detectados; com `Enter` aceita os defaults.

Se `~/.local/bin` não estiver no PATH, o installer avisa e mostra a linha a adicionar no `~/.zshrc`/`~/.bashrc`.

## Windows

Prompt de Comando (cmd):

```bat
curl -L -o install.bat https://github.com/jrunic/koine/releases/latest/download/install.bat
install.bat
```

Ou PowerShell direto:

```powershell
iwr -useb https://github.com/jrunic/koine/releases/latest/download/install.ps1 | iex
```

O `install.bat` invoca o PowerShell com `-ExecutionPolicy Bypass` inline — funciona em estações com política restritiva, sem admin. O installer usa o launcher `py -3` (ou `python`) do PATH; nada além de código-fonte Python é gravado no disco.

## Upgrade da v0.3.x (binário Go)

Rode o mesmo comando de instalação do seu sistema. O installer:

- substitui os atalhos `kn-*` da instalação Go pelos wrappers Python (o binário `kn-agente` fica órfão — pode apagar depois);
- preserva `~/.config/koine/` e `~/.local/share/koine/` intocados — arquivo do usuário, escopos, aliases, agentes e domínios continuam onde estavam. Nada a migrar;
- preserva qualquer arquivo seu que colida com um nome de wrapper (aviso em vez de sobrescrita).

A geração de contexto é equivalente à do Go — a sessão seguinte continua de onde parou.

## Atualização (v0.4.x → última)

Com o Koine já instalado, atualize com um comando:

```bash
koine atualizar
```

Resolve a última release, baixa `koine-<versao>.zip` + `SHA256SUMS`, valida o hash e reaproveita o caminho de instalação: refresca o vault shipped (preservando seus `dominios`), regenera os wrappers `kn-*` e reinstala skills nos harnesses detectados. É no-op quando você já está na última versão; `--force` reinstala mesmo assim. Roda 100% em Python — sem `.bat`/`.ps1`/powershell.

Variantes:

- `KOINE_VERSAO=vX.Y.Z koine atualizar` — vai (ou volta) para uma versão específica.
- `KOINE_BASE_URL=<url> koine atualizar` — baixa de um espelho interno (github bloqueado).

No Windows, se o download direto do github falhar por cadeia de certificado incompleta, o comando cai automaticamente para o `curl.exe` do sistema; persistindo a falha, a mensagem orienta rodar Windows Update ou usar `KOINE_BASE_URL`. Referência completa do subcomando: [referencias/cli.md](../referencias/cli.md#koine-atualizar---force).

Se a sua versão atual **não tem** o `koine atualizar` (anterior à 0.4.3), atualize uma vez pela instalação manual (seção abaixo ou o one-liner) — dali em diante `koine atualizar` basta.

## Passo a passo manual — o que os installers fazem

**Este passo a passo é exatamente o que `install.sh` (macOS/Linux) e `install.ps1` (Windows) automatizam** — o `install.bat` é só um atalho que baixa e executa o `install.ps1` com `-ExecutionPolicy Bypass`, para estações onde scripts PowerShell são bloqueados por política. Use esta seção para instalar à mão (ex.: auditoria em ambiente corporativo, máquina sem acesso direto ao GitHub) ou para entender o que roda na sua máquina. Nenhum passo exige administrador.

### 1. Localizar um Python ≥ 3.12

```bash
python3.13 -c 'import sys; print(sys.version_info >= (3, 12))'   # macOS/Linux: tente python3.13, python3.12, python3, python
py -3 -c "import sys; print(sys.version_info >= (3, 12))"        # Windows: py -3, depois python, python3
```

O comando pergunta ao próprio interpretador se ele é ≥ 3.12 — checar pela versão real, e não pelo nome, evita a pegadinha do macOS, onde `python3` é o 3.9 do sistema. Anote o caminho do interpretador aprovado (`command -v python3.13`); é ele que você usa nos passos seguintes. Se nenhum passar, instale o Python (pré-requisito acima) — nada foi tocado até aqui.

### 2. Resolver a versão a instalar

```bash
curl -fsSLI -o /dev/null -w '%{url_effective}' https://github.com/jrunic/koine/releases/latest
```

O GitHub redireciona `releases/latest` para a URL da última release — o final da URL é a tag (ex.: `v0.4.0`). Se você já sabe a versão que quer, pule este passo e use a tag direto (é o que o override `KOINE_VERSAO` faz).

### 3. Baixar o pacote

```bash
curl -fsSL --retry 3 -o /tmp/koine-0.4.0.zip \
  https://github.com/jrunic/koine/releases/download/v0.4.0/koine-0.4.0.zip
```

O asset se chama `koine-<versão sem o v>.zip` e contém duas coisas: `koine.pyz` (a aplicação — um zipapp Python, só código-fonte) e `vault/` (os arquivos de dados). Baixar para um diretório temporário garante que nada é tocado se o download falhar. Num espelho interno, troque a base da URL (é o que `KOINE_BASE_URL` faz). Para conferir integridade, o asset `SHA256SUMS` da release lista o hash de cada arquivo.

### 4. Extrair para o local canônico

```bash
python3.13 -m zipfile -e /tmp/koine-0.4.0.zip ~/.local/share/koine/dist/
```

Extrai com o módulo `zipfile` do próprio Python — não depende de `unzip` instalado. O destino canônico é o diretório de dados do Koine (`$XDG_DATA_HOME/koine/dist/`, default `~/.local/share/koine/dist/`; no Windows, `%USERPROFILE%\.local\share\koine\dist\`). Os installers limpam esse diretório antes de extrair — é área do pacote, não de dados seus; seus dados vivem em `~/.config/koine/` e não são tocados.

### 5. Rodar o instalador do produto

```bash
python3.13 ~/.local/share/koine/dist/koine.pyz instalar
```

Este é o passo que instala de fato — tudo que vem antes é transporte. O `koine instalar`:

- planta o **vault** em `~/.local/share/koine/` e os domínios em `~/.config/koine/dominios/` (arquivos idênticos são pulados; divergentes são preservados e reportados — nada seu é sobrescrito);
- gera os **wrappers** `koine` e `kn-claude`/`kn-agy`/`kn-codex`/`kn-copilot`/`kn-opencode` em `~/.local/bin/`, com o caminho absoluto do interpretador aprovado no passo 1 gravado dentro (imune a `python3` errado no PATH de amanhã);
- configura a **pasta canônica** `~/koine` com um `CONTEXTO.md` inicial e registra o alias `koine` (num terminal interativo, pergunta onde você quer a pasta);
- detecta **clientes IA** no PATH e oferece instalar as skills `kn-*` de cada um (`[S/n]`; sem terminal interativo, apenas lista e mostra o comando para depois);
- termina mostrando o comando da sua **primeira sessão**.

### 6. PATH

```bash
export PATH="$HOME/.local/bin:$PATH"    # adicione ao ~/.zshrc ou ~/.bashrc
```

```powershell
[Environment]::SetEnvironmentVariable("PATH", "$env:USERPROFILE\.local\bin;" + [Environment]::GetEnvironmentVariable("PATH", "User"), "User")
```

Os wrappers só funcionam por nome (`kn-claude ...`) se `~/.local/bin` estiver no PATH. No Unix é uma linha no profile do shell; no Windows o comando acima persiste no ambiente do usuário, sem admin. Reabra o terminal depois.

## Variantes

- **Pinar uma versão:** `KOINE_VERSAO=v0.4.0 bash install.sh` (mesmo formato no PowerShell: `$env:KOINE_VERSAO = "v0.4.0"`).
- **Espelho/proxy interno:** `KOINE_BASE_URL=<url-base-dos-assets>` aponta o download para um espelho (útil quando o firewall bloqueia `github.com`).
- **Sem nenhum interpretador permitido:** use o modo skills (`koine-skills.zip` nos assets da release) — operação sem executável e sem Python, descrita no próprio zip. Este guia não cobre esse fluxo.

## Verificação

```bash
koine versao          # esperado: koine 0.4.0
kn-claude hermes koine
```

A segunda linha gera o contexto da pasta canônica e abre o seu cliente. Dentro da sessão, `/kn-01-recebe-usuario` conclui o onboarding (tutorial completo [aqui](../tutoriais/onboarding-completo.md)).

## Problemas comuns

| Sintoma | Causa | Ação |
|---|---|---|
| `Erro: nenhum Python >= 3.12 encontrado no PATH` | Só existe Python antigo (ex.: 3.9 do macOS) ou nenhum | Instale pelo pré-requisito acima e rode o installer de novo |
| `koine: command not found` após instalar | `~/.local/bin` fora do PATH | Adicione a linha que o installer mostrou e reabra o terminal |
| Download falha (rede/firewall) | `github.com` bloqueado | Use `KOINE_BASE_URL` para um espelho interno, ou baixe `koine-<versão>.zip` manualmente e rode `python koine.pyz instalar` |
| Aviso `salvo como ....bak` durante uma sessão | Havia um arquivo seu no caminho de um artefato gerado | Nada perdido: seu arquivo está no `.bak` ao lado |
| Windows: script PowerShell bloqueado | Política de execução restritiva | Use o `install.bat` (bypass inline, sem admin) |
