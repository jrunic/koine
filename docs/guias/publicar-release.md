---
descricao: Guia para mantenedores — o ritual de release deste repositório, do gate à verificação de efeito, incluindo quando a validação em máquina de bancada é obrigatória
id: 202608291400
tipo: guia
status: ativo
tags: [guia, release, gate, teste, windows, contribuir]
---

# Guia — Publicar uma release

Audiência: mantenedores. Este é o ritual **deste** repositório, do gate ao efeito
verificado.

**Ele existe porque o ritual genérico não serve aqui.** O Koine não tem branch
`production` e não é distribuído por frota: ele vai por **tag → GitHub Release →
instaladores**, para máquina de usuário final. Quem tentar seguir o ritual de repo
de serviço tropeça já na primeira checagem — e foi o que aconteceu na v0.9.0, com
o roteiro sendo adaptado de cabeça no meio da publicação.

**Publicar é decisão de quem mantém, não efeito colateral de fechar tarefa.** O
ritual de encerramento de tarefa propõe a release e para; este guia começa depois
da autorização.

---

## 1. O gate — a lista que decide se a release pode sair

Cada item é uma medição, não uma impressão. Nenhum se pula "porque desta vez a
mudança é pequena".

### 1.1 Árvore e branch

```bash
git status --porcelain          # vazio
git rev-parse --short HEAD origin/main   # os dois iguais, depois de um fetch
```

Árvore suja significa trabalho fora da release. `HEAD` à frente significa que
falta empurrar.

### 1.2 A suíte, com o número

```bash
.venv/bin/pytest -q > /tmp/suite.txt 2>&1; echo "EXIT=$?"; tail -3 /tmp/suite.txt
```

**Duas etapas, com a saída em arquivo.** Encadear com `&&` depois de um pipe já
liberou commit com a suíte vermelha: o `grep` acha linhas, devolve `0`, e o `&&`
segue.

A suíte **é** o gate deste repo, e o relatório de release diz o número. O CI roda a
mesma suíte, mas em `ubuntu-latest` — ele **não** cobre Windows, que é justamente
onde este produto vive.

### 1.3 O bump, conferido contra a release publicada

O script de bump genérico compara `main` com `origin/production` e aqui **sai `2`**,
porque não há `production`. Isso não é falha: é o script dizendo que não se aplica.
A conferência equivalente é contra o que está publicado:

```bash
grep -m1 '^version' pyproject.toml
curl -sS https://api.github.com/repos/jrunic/koine/releases/latest | grep -m1 '"tag_name"'
```

As duas têm que **diferir**. Versão parada é release não verificável: o passo 4 fica
sem sinal para medir.

Pré-1.0, **feature vai no minor**, correção isolada no patch. `_version.py` e
`pyproject.toml` precisam concordar — o CI compara com a tag até o primeiro hífen e
**falha** se divergirem.

### 1.4 O CHANGELOG

Existe teste que cobra a seção `## [<versão>]` para versão sem hífen. Ele reprova a
suíte, então na prática este item já caiu no 1.2 — mas vale saber por que a suíte
ficou vermelha se ficar.

Numa **pré-release** o CHANGELOG não é exigido: as notas são geradas
automaticamente.

### 1.5 O gate de bancada — e quando ele é obrigatório

Aqui está a regra que faltava, e a ausência dela tem histórico: o gate foi **pulado
por decisão pelo menos três vezes** (v0.4.0, v0.4.5, v0.6.0). Não por descuido — por
não haver critério, e custo indefinido é o que se adia.

**O gate é OBRIGATÓRIO quando o diff toca:**

- **launch, wrappers ou `atualizar`** — todo defeito Windows-only já medido saiu
  daí. `WinError 193` na resolução do cliente, o finalizador do self-update, o
  `shell` do adapter, os wrappers apontando para o lugar errado.
- **escrita fora do território do Koine** — registro (`HKCU\Environment`), PATH,
  variáveis de ambiente do usuário. O que estraga aqui é do usuário, não nosso.
- **qualquer coisa que só existe no Windows** — `install.bat`, `winreg`, `ctypes`,
  resolução por `cmd /c`, codepage.
- **saída para stdout/stderr em caminho novo** — o `UnicodeEncodeError` da v0.6.3
  apareceu só com a saída redirecionada.

**O gate é DISPENSÁVEL quando o diff é comprovadamente inerte para Windows** — e a
prova é o `git diff --stat`, não a lembrança:

```bash
git diff --stat v<última>..HEAD
```

Vault, documentação, `CHANGELOG`, testes e arquivos de versão, **sem uma linha de
Python de lógica**, dispensam. Foi o critério aplicado na v0.6.0, e foi ele que
tornou o pulo defensável — o pulo sem esse critério é aposta.

**Como fazer o gate:** por **tag de pré-release**, nunca copiando o pacote à mão. O
procedimento está em [`testar-build-em-bancada.md`](testar-build-em-bancada.md), e a
razão de não improvisar é que o `instalar` grava nos wrappers o caminho **do
artefato que está executando** — validar de uma pasta descartável e apagá-la deixa
os seis wrappers apontando para o nada, sem erro na hora.

**Cada rodada de validação custa uma tag pública e permanente.** Se a validação
achar defeito, a correção exige uma tag nova — a `rc` já publicada não contém o
fix, e prova viva tem que exercitar o código que vai ser publicado. Na v0.9.0 foram
duas.

---

## 2. Publicar

```bash
git tag v<versão> && git push origin v<versão>
```

O `release.yml` dispara em tag `v*`: roda a suíte, monta `koine-<versão>.zip`
(pyz + vault), publica a Release com os instaladores, o `koine-skills.zip` e o
`SHA256SUMS`.

**Tag com hífen vira pré-release** e o `/releases/latest` a ignora — é essa a
garantia de que quem roda o one-liner nunca pega um build de teste.

### Esperar o CI da tag certa

```bash
gh run list --limit 5 --json headBranch,status,conclusion \
  -q '.[] | select(.headBranch=="v<versão>") | "\(.status) \(.conclusion // "-")"'
```

**Filtrar pelo `headBranch`.** Ler o run mais recente devolve o **anterior**
enquanto o novo não aparece — e ele costuma estar `completed success`, o que se lê
como aprovação da tag que acabou de sair.

---

## 3. Conferir que a release está como devia

```bash
gh release view v<versão> --json tagName,isPrerelease -q '"\(.tagName) prerelease=\(.isPrerelease)"'
curl -sS https://api.github.com/repos/jrunic/koine/releases/latest | grep -m1 '"tag_name"'
```

**O `latest` se confere pela API, não pelo redirect.** O redirect HTML de
`/releases/latest` é **cacheado**: depois de publicar, ele ainda responde a versão
anterior por um tempo. Os instaladores resolvem a versão por esse redirect, então o
atraso é real para o usuário — mas quem verifica a release não pode confundir cache
com falha de publicação.

Numa release estável, `latest` **tem** que mover. Numa pré-release, **não** pode.

---

## 4. Verificar o efeito — contra o artefato baixado

O passo que se perde quando não há ritual. "O CI ficou verde" afirma sobre o
processo; release verificada afirma sobre o **artefato publicado**.

### 4.1 O artefato é o que se diz que é

```bash
curl -fsSLO https://github.com/jrunic/koine/releases/download/v<versão>/koine-<versão>.zip
curl -fsSLO https://github.com/jrunic/koine/releases/download/v<versão>/SHA256SUMS
grep koine-<versão>.zip SHA256SUMS | shasum -a 256 -c -
unzip -q koine-<versão>.zip -d pkg
HOME=$(mktemp -d) python3 pkg/koine.pyz versao
```

**Em HOME isolado**, e **de fora de qualquer checkout** — dentro do repositório o
comando pode resolver o código local em vez do publicado.

### 4.2 O que esta release deveria mudar, mudou?

Nomear o sinal **antes** e medi-lo depois, executando **de dentro do pyz publicado**:

```bash
PYTHONPATH=pkg/koine.pyz python3 -c "<exercita o comportamento novo>"
```

Verificar que o arquivo está no zip **não** é verificar comportamento. Na v0.9.0 os
sinais foram: a escadinha de shell decidindo por execução, cada adapter declarando o
que aceita, a decisão de pré-requisitos com a estação travada simulada, e o PATH
preservando duplicata de terceiro.

Sem sinal nomeado, a release "passou" apenas porque nada explodiu.

---

## 5. Registrar

- Comentário nas tarefas que a release carrega — versão, o que a verificação mediu,
  e o link da Release.
- Roadmap: o item marcado em produção, com a data.
- Se o gate de bancada rodou, **conferir os seis wrappers** da conta usada depois de
  apagar qualquer pasta de validação. Verificar faz parte da limpeza, não só do
  teste.

---

## Regras duras

- **A suíte é o gate, e o número vai no relatório.** Gate que não se nomeia passa por
  verificado sem ter sido.
- **Versão avança em toda release**, e as duas fontes concordam com a tag.
- **O gate de bancada se pula por critério medido (`git diff --stat`), nunca por
  pressa.**
- **Não se copia o pacote para a máquina de teste** — tag de pré-release, sempre.
- **`latest` se confere pela API.**
- **Verificar o efeito, não o processo** — e contra o artefato baixado, não contra a
  árvore local.
