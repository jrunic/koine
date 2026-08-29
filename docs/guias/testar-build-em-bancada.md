---
descricao: Guia para mantenedores — como levar um build de desenvolvimento para uma máquina de teste usando tag de pré-release, em vez de montar o koine.pyz à mão
id: 202608271800
tipo: guia
status: ativo
tags: [guia, release, teste, windows, contribuir]
---

# Guia — Testar um build em máquina de bancada

Audiência: mantenedores que precisam validar uma mudança numa máquina que não é a
de desenvolvimento — tipicamente Windows, onde o CI é POSIX-only e não pega
defeito Windows-only.

**A regra:** o build de teste vai por **tag de pré-release**, instalado pelo
instalador de verdade. Não se copia `koine.pyz` para a máquina de teste.

## Por que não copiar o pyz à mão

Foi o que se fazia até 27/08/2026, e custou uma sessão de diagnóstico:

- **O caminho de produção não era exercitado.** O que o usuário faz — baixar o
  asset, conferir o `SHA256SUMS`, extrair no layout de `~/.local/share/koine`,
  gerar os wrappers — nada disso era testado. Testava-se um arranjo que só existe
  na bancada.
- **O teste produzia defeitos próprios.** `koine instalar` bakeia nos wrappers o
  pyz que está executando (`_pyz_padrao()` devolve `sys.argv[0]`). Isso está
  **certo** para quem instala a partir do zip — e vira um laço quando os wrappers
  já apontam para um pyz de bancada: chamado por eles, o `instalar` só pode
  reescrever para o mesmo lugar. Sair do laço exige invocar o pyz instalado **e**
  passar `--pyz`, as duas pontas.
- **Diretório compartilhado quebra o isolamento.** Um pyz numa pasta gravável por
  outra conta é executado pela conta restrita — que é justamente a que representa
  o ambiente do usuário final.

## O procedimento

### 1. Bump da versão, na branch de desenvolvimento

O CI compara a tag com a versão do pacote e **falha** se divergirem. Para a tag
`v0.7.0-rc1`, `_version.py` e `pyproject.toml` precisam dizer `0.7.0` — a
comparação usa a tag até o primeiro hífen.

### 2. Tag com hífen

```bash
git tag v0.7.0-rc1 && git push origin v0.7.0-rc1
```

**Qualquer tag com hífen vira pré-release** (`release.yml`, passo *Detect
pre-release*), e o CI publica a release marcada como tal. Numa pré-release o
`CHANGELOG` não é exigido: as notas são geradas automaticamente.

### 3. Instalar na máquina de teste, pelo instalador de verdade

```cmd
set KOINE_VERSAO=v0.7.0-rc1
install.bat
```

No Unix: `KOINE_VERSAO=v0.7.0-rc1 bash install.sh`. O nome do asset é montado a
partir da tag (`koine-0.7.0-rc1.zip`), e é assim que o CI o publica.

### 4. Conferir que `latest` não se moveu

```bash
curl -fsSLI -o /dev/null -w '%{url_effective}\n' \
  https://github.com/jrunic/koine/releases/latest
```

Tem que responder a última release **estável**. O `/releases/latest` do GitHub
ignora pré-releases — é essa a garantia de que um usuário rodando o one-liner
nunca pega uma tag de teste. Garantia não medida é promessa: confira depois de
publicar a tag, não antes.

## O que verificar na máquina de teste

- **Todos os wrappers, não um.** São seis (`koine` + um `kn-<cliente>` por
  adapter). Um defeito que atinge só o `kn-codex.bat` passa por resolvido se
  alguém olhar só o `kn-claude.bat`.
- **`koine versao`** responde a versão esperada — de fora de qualquer checkout.
  Dentro do repositório, o comando pode resolver o código local em vez do
  instalado.
- **O caminho que o wrapper bakeou** (`type kn-claude.bat` no Windows,
  `cat ~/.local/bin/kn-claude` no Unix) aponta para a instalação, não para uma
  pasta de bancada.

## Ao aposentar uma bancada, procure o que aponta para ela

Apagar a pasta não basta. Medido em 28/08/2026, ao retirar a bancada da VM: havia
uma **tarefa agendada** (`kn-diag`) apontando para um `.bat` dentro dela, que rodava
`koine.pyz instalar` **do pyz da bancada**. Como o `instalar` bakeia nos wrappers o
pyz que está executando, aquele job **desfazia a instalação boa toda vez que
rodava** — e tinha rodado na noite anterior, revertendo os seis wrappers que eu
havia acabado de verificar.

Duas consequências práticas:

- **Antes de apagar, liste o que referencia a pasta** — tarefas agendadas, atalhos,
  entradas de PATH, `Run` do registro. Uma pasta apagada com um job vivo apontando
  para ela troca um problema silencioso por outro barulhento.
- **Verifique de novo depois de mexer.** Uma medição de wrappers vale para o
  instante em que foi feita; o que a invalidou aqui foi um job noturno, não uma ação
  humana.

Para consertar wrappers que já foram bakeados para o lugar errado, use a forma das
**duas pontas** — invocar o pyz instalado **e** passar `--pyz` apontando para ele:

```cmd
"%USERPROFILE%\AppData\Local\Python\...\python.exe" ^
  "%USERPROFILE%\.local\share\koine\dist\koine.pyz" ^
  instalar --pyz "%USERPROFILE%\.local\share\koine\dist\koine.pyz" < NUL
```

O `< NUL` não é enfeite: sem ele o `instalar` entra no modo interativo, para no
prompt da pasta canônica e o comando fica pendurado sem erro.

## Reincidiu em 28/08/2026, e não foi por um job

A seção acima descreve o caso da tarefa agendada. O de 28/08 foi mais simples e mais
difícil de ver: **o mantenedor** validou dois incrementos rodando `koine instalar` a partir
de um pyz em `C:\Users\Public\<pasta-de-medição>`, e depois apagou a pasta na limpeza. Os
seis wrappers das duas contas ficaram apontando para um arquivo inexistente, e a instalação
de uma delas passou horas quebrada sem que nada reclamasse — o defeito só aparece quando
alguém chama um `kn-<cliente>`.

Duas coisas que isso ensina sobre este guia:

- **A regra não é sobre conforto, é sobre não estragar a bancada.** Copiar o pyz parece
  atalho barato porque a medição em si funciona; o que quebra é o que fica para trás.
- **Verificar o wrapper faz parte da limpeza, não só do teste.** A lista de "o que verificar"
  acima vale de novo **depois** de apagar qualquer pasta usada na validação.

Se a validação for pequena demais para justificar uma tag, o caminho é `KOINE_BASE_URL`
apontando para um espelho — não copiar o pyz.

## Onde este guia entra

Ele cobre **como** levar um build para a máquina de teste. **Quando** esse gate é
obrigatório — e quando se pode pular com critério — está no
[`publicar-release.md`](publicar-release.md), junto do ritual de release inteiro.

## Ressalvas

- **Tag de teste é pública e permanente.** O repositório é público, e
  `v0.7.0-rc1` fica na lista de releases para sempre. É o custo aceito —
  pré-release é convenção conhecida. A alternativa sem tag é `KOINE_BASE_URL`
  apontando para um espelho, que os dois instaladores aceitam.
- **Cada build de validação custa uma tag.** O workflow dispara em tag `v*`, em
  PR para `main` e em `workflow_dispatch` — não em push de branch.
