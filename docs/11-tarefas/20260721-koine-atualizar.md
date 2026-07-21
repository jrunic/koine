---
id: 202607211230
projeto: koine
tipo: spec
status: aprovado
tags: [spec, koine, atualizar, self-update, distribuicao]
---

# Spec: comando `koine atualizar`

> Fora do roadmap (repo sem `roadmap.md` — caminho curto autorizado pelo Orlando nesta sessão). Alvo de release: v0.4.3.

## Problema

Hoje só existe caminho de **primeira instalação**: o usuário baixa e roda `install.sh`/`install.ps1`/`install.bat`, que resolvem a release, baixam `koine-<versao>.zip`, extraem no diretório de dados e delegam ao `koine instalar`. Para **atualizar** uma instalação existente, o usuário precisa reexecutar o instalador externo — reobter o script, ter `curl`/`bash`/`powershell`, e lembrar do procedimento. Não há um comando de primeira classe dentro do próprio Koine.

Quem sente: todo usuário instalado que quer subir de versão — em especial em **ambiente corporativo travado** (ex.: Grupo Aldo), onde reexecutar um script externo com `curl`/`bash` é atrito. Nesse ambiente o github **não** é bloqueado; o que a política bloqueia é o **download de executáveis (`.exe`)**. Como a distribuição do Koine é um `.zip` (pyz + vault, sem `.exe`/código nativo — a razão do port Python), tanto a resolução da versão quanto o download do pacote pelo github continuam viáveis lá.

## Solução

Adicionar o subcomando `koine atualizar`: resolve a versão-alvo (última release por padrão, ou fixada), baixa e valida o pacote de distribuição, e aplica a atualização reaproveitando o caminho de instalação já existente (extração para o diretório de dados + regeneração de wrappers). Implementado em Python puro (stdlib), sem depender de `curl`/`bash`/`powershell` externos, honrando os mesmos overrides de espelho e versão dos instaladores (`KOINE_BASE_URL`, `KOINE_VERSAO`). A atualização não sobrescreve o pacote em execução: baixa para área temporária e faz a troca via um processo da versão nova.

## Histórias de Usuário

1. Como usuário com Koine instalado, quero rodar `koine atualizar` e receber a versão mais recente, para não repetir o procedimento manual de instalação.
2. Como usuário já na versão mais recente, quero que `koine atualizar` me diga isso e não faça nada, para não baixar nem reinstalar à toa.
3. Como usuário em rede corporativa que bloqueia download de `.exe` (ex.: Grupo Aldo), quero que `koine atualizar` resolva a versão pelo github e baixe o pacote `.zip`, para atualizar sem esbarrar na política de executáveis.
4. Como administrador com espelho interno, quero poder redirecionar o download (`KOINE_BASE_URL`) e fixar a versão (`KOINE_VERSAO`), para cenários de mirror ou ar-gapped — capacidade genérica, não obrigatória no Aldo.
5. Como usuário sem rede no momento, quero que uma falha de download deixe minha instalação atual intacta e me oriente, para nunca ficar com uma instalação quebrada pela metade.
6. Como usuário no Windows, quero que a atualização funcione mesmo com o pacote atual "em uso", para não receber erro de arquivo bloqueado.
7. Como usuário, quero fixar uma versão específica (`koine atualizar` com `KOINE_VERSAO`) inclusive para voltar a uma anterior, para controlar exatamente o que instalo.
8. Como usuário que atualizou, quero que os skills novos que vieram no vault sejam instalados nos meus harnesses, para não ter de rodar `koine instalar-habilidades` à mão depois de cada atualização.

## Critérios de Sucesso

- Rodar `koine atualizar` já estando na versão-alvo resolvida: sai com código 0, imprime que já está na versão X e **não baixa nem reinstala** (nenhuma escrita em `dist/`). Com `--force`, reinstala a mesma versão.
- Rodar `koine atualizar` com versão nova disponível: ao final, `koine versao` reporta a nova versão e os wrappers `kn-*` invocam o pacote novo.
- Falha de resolução/download (sem rede, DNS, proxy, 404): sai com código ≠ 0, `koine versao` permanece **inalterado**, nenhum resíduo parcial em `dist/`, e a mensagem orienta a causa e a saída (ex.: fixar `KOINE_VERSAO`, conferir `KOINE_BASE_URL`).
- A atualização baixa **apenas** o asset `.zip` (nunca um `.exe`), atendendo a política corporativa que bloqueia executáveis (caso Grupo Aldo).
- Após a troca do pacote, um skill novo presente no vault novo passa a existir na pasta de skills de **cada harness detectado** (binário no PATH); skills idênticos ficam inalterados; skills customizados pelo usuário (divergentes) são preservados e reportados, salvo `--force`. Verificável adicionando um `kn-*` à release falsa e conferindo a pasta de skills de um harness detectado.
- Com `KOINE_BASE_URL` apontando para um espelho: o download vem do espelho, não do github (verificável servindo uma release falsa num host local — mesmo harness do e2e de instalação existente).
- A atualização **não sobrescreve o pacote a partir do qual está executando**: sem erro de "arquivo em uso" no Windows e sem `ImportError` de módulo carregado tarde no Unix.
- Integridade: quando o `SHA256SUMS` da release está disponível, o pacote baixado é verificado contra o hash publicado antes de ser aplicado; hash divergente aborta sem tocar a instalação atual.
- Cross-platform: o comando cumpre os critérios acima em macOS, Linux e Windows **sem** exigir `curl`, `bash` ou `powershell` no PATH.
- **Execução 100% dentro do koine (Python)**: durante um `koine atualizar` nenhum processo `powershell`, `cmd`, `.bat` ou `.ps1` é criado, e os instaladores shell (`install.sh`/`ps1`/`bat`) não são invocados. O único subprocesso admissível é o próprio interpretador Python (`sys.executable`), usado no handoff da auto-troca. É a fronteira rígida do Grupo Aldo (powershell bloqueado por AppLocker) — verificável observando os processos-filho durante a execução.

## Decisões de Implementação

- **Novo módulo de atualização** — encapsula resolução de versão-alvo, download, verificação de integridade e o handoff da troca. Interface pequena (uma entrada "atualizar para a versão-alvo"), implementação rica; ponto de costura entre "obter o pacote" (novo) e "aplicar o pacote" (reuso do instalar).
- **Novo subcomando na CLI** — `atualizar` entra no conjunto de subcomandos e no despacho, com handler próprio; segue a convenção PT-BR dos demais (`instalar`, `mostrar`, `versao`).
- **Reuso do caminho de instalação** — a aplicação efetiva (extração para o diretório de dados + regeneração de wrappers com interpretador bakeado + reconhecimento de instalação anterior) reaproveita o fluxo do `instalar`, não o reimplementa.
- **Refresh de skills nos harnesses detectados** — diferente do `instalar` não-interativo (que só informa), o `atualizar` **instala** skills automaticamente, porque o próprio comando já é o opt-in explícito do usuário. Reaproveita a detecção de harnesses (binário no PATH) e a cópia idempotente de skills existentes (idênticos pulados, divergentes preservados e reportados salvo `--force`). Assim, skills novos do vault entram sem passo manual; customizações não são clobbered.
- **Resolução da versão-alvo** — precedência: `KOINE_VERSAO` fixa a tag; senão resolve a última release pública pelo github (que está acessível inclusive no Aldo — só o download de `.exe` é bloqueado, e o pacote é `.zip`). `KOINE_BASE_URL` redireciona apenas o download, para cenários de espelho/ar-gapped; não é necessário no Aldo.
- **Baixa só o `.zip`, nunca `.exe`** — a atualização obtém exclusivamente o asset `koine-<versao>.zip` (pyz + vault). Compatível com políticas corporativas que bloqueiam executáveis; é a mesma propriedade que motivou o port Python.
- **Convenção de URL e overrides idênticos aos instaladores** — mesma montagem `<base>/<tag>/koine-<versao>.zip`, mesmos overrides `KOINE_BASE_URL`/`KOINE_VERSAO`. A lógica de fetch é reimplementada em Python (não se reinvocam os scripts shell); a paridade da convenção com os instaladores é travada por teste.
- **Download stdlib-only** — obtenção via biblioteca padrão (HTTP/TLS da stdlib), sem dependência externa nova e sem código nativo (mantém a restrição-âncora da distribuição).
- **Auto-substituição segura, sem trampolim de shell** — o pacote é baixado e extraído para área temporária; a troca para o diretório de dados e a regeneração de wrappers acontecem sob o **processo da versão nova**, lançado como o próprio interpretador Python (`sys.executable`) — **nunca** via `.bat`/`.cmd`/`.ps1` ou powershell (o padrão clássico de trampolim batch no Windows é explicitamente proibido aqui pela fronteira do Aldo). Evita sobrescrever o pacote em execução; falha antes do commit final não altera a instalação vigente (sem estado parcial).
- **Toda a cadeia é Python in-process** — resolução de versão, download e extração usam a biblioteca padrão (HTTP/TLS e `zipfile`), não `curl`/`unzip`/`Expand-Archive`; o refresh de skills e a regeneração de wrappers reaproveitam o código de instalação, que já é puro-Python sem shell-out. Os scripts `install.sh`/`ps1`/`bat` não são reinvocados.
- **Verificação de integridade** — quando o manifesto de somas (`SHA256SUMS`) da release está disponível, valida o hash do pacote antes de aplicar; ausência do manifesto degrada para "sem verificação" com aviso, não bloqueia.
- **Comparação de versão** — igualdade entre a versão instalada (fonte única já existente) e a versão-alvo resolvida decide o no-op; `--force` reinstala mesmo se iguais.

## Decisões de Teste

- **Bom teste = comportamento externo observável**, não detalhe de implementação: versão reportada antes/depois, no-op quando já na versão-alvo, instalação intacta após falha de rede, origem do download sob espelho.
- **e2e reaproveitando o harness de instalação existente** — servidor HTTP local servindo uma release falsa, com `KOINE_BASE_URL`/`KOINE_VERSAO` apontando para ele; exercita o comando de ponta a ponta (subprocess do pacote), afirmando a versão pós-atualização e o no-op.
- **Falha sem estado parcial** — simular download indisponível e afirmar que a versão instalada não muda e `dist/` não fica com resíduo.
- **Paridade de convenção com os instaladores** — travar que a URL/versão montadas pelo comando batem com a convenção dos scripts de release.
- **Prior art:** `tests/test_installer_e2e.py` (release falsa + overrides), `tests/test_pyz_e2e.py` e `tests/test_cli_e2e.py` (subprocess do pacote/subcomandos), `tests/test_versao.py` (fonte única da versão).

## Fora de Escopo

- **Auto-atualização / verificação em segundo plano** — o comando só age quando invocado explicitamente. Sem checagem automática de novas versões.
- **Ponteiro de "latest" no espelho** — publicar/consumir um marcador de última versão no `KOINE_BASE_URL` para resolução automática 100% offline (ar-gapped puro). Não é necessário para o Aldo (github acessível); no espelho, fixa-se `KOINE_VERSAO`. Registrado como evolução futura.
- **Rollback além de fixar versão** — não há histórico/undo próprio; voltar de versão é fixar `KOINE_VERSAO` de uma release anterior.
- **Atualizar os próprios scripts instaladores** (`install.sh`/`ps1`/`bat`).
- **Assinatura criptográfica (GPG/sigstore)** — verificação de integridade se limita à soma `SHA256` publicada.
- **Migração de dados do usuário** — `~/.config/koine/` (escopos, agentes, aliases) não é tocado; a atualização é do pacote da aplicação.
- **Poda de skills removidos** — skills que existiam e saíram do vault novo **não** são apagados das pastas dos harnesses; o refresh só adiciona/atualiza. Limpeza de skills obsoletos fica para evolução futura.
- **Instalar skills em harness não detectado** — o refresh cobre só harnesses com binário no PATH; não instala para clientes ausentes nem prompta por novos.

## Assumptions

1. A atualização cobre o **pacote da aplicação** (pyz + vault) **e** o refresh de skills: instala/atualiza os skills do vault novo em **todos os harnesses detectados** (binário no PATH), idempotente, preservando customizações do usuário salvo `--force`. Skills **removidos** do vault não são podados (ver Fora de Escopo).
2. No Grupo Aldo o github é acessível (só o download de `.exe` é bloqueado; o pacote é `.zip`), então "latest" resolve pelo github normalmente. `KOINE_BASE_URL`/`KOINE_VERSAO` cobrem espelho/ar-gapped como capacidade genérica, não como requisito do Aldo.
3. Verificação de integridade usa o `SHA256SUMS` da release; se ausente, prossegue com aviso.
4. HTTP/TLS da stdlib basta para baixar do github e de espelhos internos (cadeia de certificados do sistema); sem dependência externa nova.
5. Python 3.12+ (padrão da frota); zero código nativo mantido.
6. `koine atualizar` permite fixar versão anterior (downgrade explícito via `KOINE_VERSAO`) — não há trava de "só avançar".
7. Alvo de release da própria feature: v0.4.3 (bump de `pyproject`/`_version` + entrada no CHANGELOG no tail do dev-04).
8. Fronteira do Grupo Aldo, precisa: bloqueados = **download de `.exe`** (a distribuição é `.zip`, ok) e **execução de `powershell.exe`** (AppLocker). **Não** bloqueado = execução de `python.exe` (o koine roda sobre ele) nem download de `.zip`. Logo o handoff da auto-troca via `sys.executable` é permitido; qualquer passo por `.bat`/`.cmd`/`.ps1`/powershell é proibido.

→ Me corrige agora ou sigo com isso para o `dev-03-escreve-plano`.

## Notas

- Risco principal: **auto-substituição do pacote em execução** (arquivo em uso no Windows; import tardio no Unix). No Windows o processo `atualizar` mantém `dist/koine.pyz` aberto, então a troca não pode ocorrer enquanto ele vive: o padrão é o pai lançar a versão-filha **destacada** e sair, e a filha esperar o arquivo liberar antes do `os.replace` — tudo em Python, sem trampolim batch. Precisa de teste explícito no dev-04.
- **Fronteira de atomicidade**: falha de resolução/download/verificação é totalmente segura (acontece em temp; `dist` e wrappers intocados). A **fase de aplicação** (troca do pyz → extração do vault → wrappers → skills) não é transacional; uma falha no meio é **recuperável re-rodando** (o caminho de instalação é idempotente), não revertida automaticamente. O critério "sem estado parcial" vale para a fase de fetch; a fase de aplicação garante recuperabilidade por re-execução.
- Duplicação inevitável da convenção de fetch entre os instaladores (shell/ps) e este comando (Python), por não compartilharem código. Contida por teste de paridade de convenção.
- Dependência futura: se o "latest via espelho" entrar, exige infra do lado do espelho (publicar o ponteiro) — decisão de distribuição, não só de código.
- Backlink: fix de resolução de agente da mesma release em [`../../CHANGELOG.md`](../../CHANGELOG.md) (seção Unreleased → 0.4.3).
