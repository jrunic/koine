---
descricao: Guia de instalação do Koine v0.4.x — macOS, Linux e Windows; upgrade da v0.3.x (Go); versão pinada e espelho; verificação e solução de problemas
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
