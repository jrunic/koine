---
descricao: Catálogo de erros conhecidos do Koine e de clientes de IA de terceiros que ele orquestra — sintoma, causa e remédio, mantido fora do ciclo de release
id: 202609192210
tipo: referencia
status: ativo
projeto: koine
escopo: repo:koine
plataforma: "*"
dominios: [tecnologia]
tags: [referencia, koine, erro, suporte, diagnostico]
---

# Referência — Erros conhecidos

Consultado pela `/kn-17-trata-erro` sempre pela versão mais recente da branch
`main` (`raw.githubusercontent.com/jrunic/koine/main/docs/referencias/erros-conhecidos.md`)
— uma correção documentada aqui vale imediatamente para toda sessão que a
consultar, sem depender de nova versão do Koine ser publicada ou instalada.

Cada entrada segue o mesmo formato: **Sintoma** (o que a pessoa vê, com o
texto do erro quando existe um), **Causa**, **Remédio** (o passo a passo que
a skill aplica ou orienta o mentorado a aplicar).

## `WinError 193` ao abrir sessão no Windows

**Sintoma:** o comando `kn-<cliente>` falha com uma mensagem citando
`WinError 193` (algo como "não é um aplicativo Win32 válido").

**Causa:** versões do Koine anteriores à v0.4.2 resolviam o cliente pelo
caminho binário devolvido por uma busca no PATH, e o Windows recusa executar
esse caminho mesmo quando o mesmo comando digitado no terminal funciona. A
partir da v0.4.2 o launch resolve pelo **nome**, via `cmd /c`, com a mesma
resolução do shell interativo.

**Remédio:** `koine atualizar`. Se o erro persistir depois de atualizar,
não é este caso — vai para o relato.

## Saída quebrada (`UnicodeEncodeError`) quando a saída é redirecionada no Windows

**Sintoma:** `koine instalar` (ou outro comando) trava com
`UnicodeEncodeError` mencionando um caractere como `✓`, só quando a saída
está sendo redirecionada para arquivo, pipe ou tarefa agendada — no console
interativo funciona.

**Causa:** com stdout em console o Windows aceita Unicode direto; redirecionado,
o encoding cai para `cp1252`. Corrigido na v0.6.3 (`koine.saida.preparar`
mantém o encoding do ambiente e troca a política de erro para substituir
caracteres não suportados, em vez de travar).

**Remédio:** `koine atualizar`.

## `install.bat` recusa com "Acesso negado" citando PowerShell

**Sintoma:** o instalador `.bat` do Windows falha citando
`powershell.exe` e política de execução, numa máquina corporativa que
bloqueia o PowerShell.

**Causa:** versões do instalador anteriores à v0.6.2 chamavam
`powershell -ExecutionPolicy Bypass` por dentro do `.bat`. A partir da
v0.6.2 o `install.bat` é 100% `cmd.exe`, sem depender de PowerShell.

**Remédio:** baixar o instalador mais recente do
[README do produto](https://github.com/jrunic/koine#readme) — o link do
one-liner sempre aponta para a última versão publicada — e rodar de novo.

## OpenCode trava com `Unexpected server error` no Windows

**Sintoma:** ao abrir sessão pelo `kn-opencode`, o cliente responde
`Unexpected server error` (ou fica preso sem responder) logo na primeira
interação, no Windows.

**Causa:** o OpenCode sonda qual shell usar e pode escolher um executável de
PowerShell presente no PATH mas que não executa de fato (recusado por
política de grupo) — a sondagem via presença engana onde só a execução real
revela o problema. Corrigido na v0.16.1: o adapter do OpenCode passa a forçar
`"shell": "cmd"` no Windows, sem depender da sondagem do próprio cliente.

**Remédio:** `koine atualizar` para v0.16.1 ou mais recente.

## Codex CLI falha em toda chamada de ferramenta com `os error 2`

**Sintoma:** a sessão do Codex abre e responde normalmente, mas **toda**
chamada de ferramenta (ler arquivo, rodar comando) devolve um erro citando
`os error 2`.

**Causa:** defeito de instalação do próprio Codex CLI, não do Koine — o
pacote `codex-<arquitetura>-pc-windows-msvc.exe.zip`, frequentemente o
primeiro que aparece na página de releases, não inclui o executável
`codex-code-mode-host.exe`, sem o qual toda ferramenta falha fechado.

**Remédio:** reinstalar o Codex a partir do pacote
`codex-package-<arquitetura>....tar.gz` (não o `.exe.zip`) na página de
releases do Codex CLI — esse pacote inclui o host de ferramentas.

## `CONTEXTO.md` sem `escopo:` derruba a sessão pedindo para editar YAML

**Sintoma:** abrir sessão numa pasta com `CONTEXTO.md` existente e legível
termina com um erro mandando editar o frontmatter à mão.

**Causa:** versões do Koine anteriores à v0.4.5 (o auto-guiar de pasta) e à
v0.6.1 (o estado `INCOMPLETO` para pasta sem `escopo:`) tratavam qualquer
frontmatter fora do estritamente válido como motivo para abortar a sessão.
Desde então, o launch classifica o estado da pasta e conduz a correção
conversando, sem tocar no arquivo.

**Remédio:** `koine atualizar`. Se a versão já for recente e o erro persistir,
não é este caso — vai para o relato.

## Confusão entre `paseo.exe` e `paseo.cmd` ao configurar o Paseo

**Sintoma:** ao configurar o acesso remoto pelo Paseo numa máquina Windows
nova, um comando `paseo <algo>` não responde como esperado, ou abre o
aplicativo em vez de executar o comando.

**Causa:** o instalador do Paseo no Windows cria dois executáveis com nomes
parecidos — `paseo.exe` é a instância do **aplicativo** (a interface); o CLI
que os comandos do Koine chamam é `paseo.cmd`. Confundir os dois faz um
comando de CLI abrir a interface gráfica, ou vice-versa.

**Remédio:** os comandos `koine paseo-*` já resolvem isso automaticamente
(`src/koine/paseo_ambiente.py` procura o `paseo.cmd`, nunca o `.exe`, com
fallback para o local padrão de instalação). Se um comando `koine paseo-*`
funcionar mas uma tentativa manual de rodar `paseo` direto no terminal
confundir os dois, é esperado — usar sempre os comandos `koine paseo-*`, não
`paseo` direto.

## OpenCode falha com `EUNKNOWN: unknown error, uv_spawn` ao carregar uma skill

**Sintoma:** a sessão do OpenCode responde normalmente e executa comandos de
terminal (`cmd.exe` funciona), mas carregar qualquer skill — inclusive com a
flag `--pure` — falha com um erro citando `uv_spawn` (às vezes
`EUNKNOWN: unknown error, uv_spawn`). Listar as skills disponíveis e ler um
arquivo direto continuam funcionando; só o carregamento de uma skill falha.

**Causa:** bug do próprio OpenCode, não do Koine. A ferramenta nativa `skill`
do OpenCode lista os arquivos da skill usando o binário `rg` (ripgrep) por
baixo. Na primeira vez que precisa dele, o OpenCode baixa o arquivo `.zip` do
ripgrep e extrai usando **exclusivamente PowerShell**
(`powershell.exe`/`pwsh.exe -Command Expand-Archive`), sem nenhum caminho
alternativo. Numa máquina Windows onde a execução de PowerShell é negada por
política (GPO/AppLocker — o mesmo perfil corporativo que o Koine já trata em
outros pontos desta referência), essa chamada é recusada pelo Windows na
criação do processo, com um código de erro que a camada de execução do
OpenCode não sabe nomear — e é isso que aparece como `uv_spawn`. O campo
`"shell"` que o adapter do OpenCode do Koine grava não tem efeito aqui: o
download e a extração do ripgrep não leem essa configuração.

**Remédio:** instalar o `rg.exe` manualmente numa pasta que já esteja no
`PATH` — o OpenCode usa um `rg` já disponível no `PATH` antes de tentar
baixar e extrair o dele. Com `cmd.exe` (sem PowerShell):

```
curl -sSL -o %TEMP%\rg.zip https://github.com/BurntSushi/ripgrep/releases/download/15.1.0/ripgrep-15.1.0-x86_64-pc-windows-msvc.zip
tar -xf %TEMP%\rg.zip -C %TEMP%\rg-extraido
copy %TEMP%\rg-extraido\ripgrep-15.1.0-x86_64-pc-windows-msvc\rg.exe %USERPROFILE%\.local\bin\rg.exe
```

(`tar` já vem no Windows 10/11 e não depende de PowerShell — troque
`x86_64` por `aarch64` numa máquina ARM64.) A pasta `%USERPROFILE%\.local\bin`
já é onde o `instalar` do Koine coloca os próprios wrappers e já está no
`PATH` do usuário; se o Koine ainda não tiver sido instalado nesta máquina,
qualquer pasta já presente no `PATH` serve. Depois de copiar o `rg.exe`,
tentar carregar a skill de novo.

## Koine (ou Paseo) instalado, mas o comando não é reconhecido na sessão atual

**Sintoma:** logo depois de `koine instalar` (ou de instalar o Paseo), um
comando novo (`koine`, `kn-<cliente>`, `paseo`) não é reconhecido pelo
terminal, embora o instalador tenha terminado sem erro.

**Causa:** o instalador acrescenta a pasta do comando ao `PATH` do usuário
(via registro, no Windows), mas o terminal já aberto no momento da instalação
carregou o `PATH` **antes** dessa mudança — só uma sessão de terminal nova
enxerga o valor atualizado.

**Remédio:** fechar e reabrir o terminal (ou a sessão), e tentar de novo. Se
o comando ainda não for reconhecido depois de reabrir, não é este caso — vai
para o relato.
