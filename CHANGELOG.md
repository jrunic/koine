# Changelog

All notable changes to Koine are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.3] — 2026-07-21

### Added

- **Comando `koine atualizar`** — self-update para a última release (ou versão fixada em `KOINE_VERSAO`), baixando o `.zip` do github (ou de `KOINE_BASE_URL`), verificando `SHA256SUMS`, e reaproveitando o caminho de instalação: refresca o vault shipped preservando os `dominios` do usuário, regenera os wrappers e reinstala skills nos harnesses detectados. Execução 100% Python — nenhum `.bat`/`.ps1`/powershell — para políticas que bloqueiam executáveis e powershell (ex.: Grupo Aldo). Auto-troca do pyz é in-process no POSIX e delegada a um processo-filho da versão nova no Windows (stdio em log, sem trampolim batch). No-op quando já na versão-alvo; `--force` reinstala.

### Fixed

- **Agente de usuário não carregava (regressão do port Python)** — `contexto.resolver` procurava agentes só em `vault/agentes` (`~/.local/share/koine/`), onde vive apenas o `hermes` distribuído. Agentes criados pela `kn-03-cria-agente` moram em `config/agentes` (`~/.config/koine/`) e nunca eram achados — em qualquer OS. O path era montado sem validar existência, então seguia silencioso e o agente simplesmente não entrava no contexto da sessão. A série Go lia do `config` (por isso o defeito não aparecia até rodar o build Python). Agora `_achar_agente` busca `config/agentes` primeiro (override do usuário) e `vault/agentes` depois (distribuído). Afeta os 5 adapters — `resolver` é compartilhado.
- **Resolução do agente é case-insensitive** — o nome vinha do arg do CLI com a caixa crua (`Leia`), mas o slug em disco é lowercase (`leia.md`). Casar por caixa crua só resolvia em FS case-insensitive (macOS/Windows), sumindo o agente em FS case-sensitive (Linux/OpenClaw). O match agora ignora caixa contra os arquivos reais.

### Changed

- **Agente ausente falha alto** — nome que não casa com nenhum agente agora levanta `AgenteNaoEncontrado` (tipada, carrega o nome pedido + lista de disponíveis unindo usuário e distribuídos); `cli`/`mensagens` decidem prosa e política. Antes: path inexistente propagado em silêncio. Padrão `ClienteNaoEncontrado`/`ClienteNaoExecutavel`.

## [0.4.2] — 2026-07-16

### Fixed

- **Windows WinError 193 (resolução robusta do cliente)** — no Windows o launch agora invoca o cliente via `cmd /c <cliente>` pelo nome, deixando o `cmd.exe` aplicar a mesma resolução PATHEXT do shell interativo. O guard `.bat`/`.cmd` da 0.4.1 não bastava: o `shutil.which` podia devolver uma variante que o `CreateProcess` recusava (WinError 193) mesmo havendo um `.cmd`/`.exe` válido ao lado. Se o cliente roda quando digitado no terminal, agora roda pelo `kn-<cliente>`.

### Changed

- **Erros de lançamento amigáveis** — cliente ausente no PATH e cliente encontrado-mas-não-executável agora produzem mensagens orientadas (diagnóstico + correção por OS) em vez de traceback Python. Exceções tipadas (`ClienteNaoEncontrado`, `ClienteNaoExecutavel`) carregam dados; a prosa vive em `mensagens`.

## [0.4.1] — 2026-07-16

### Fixed

- **Windows WinError 193** — `launch.lancar` agora envolve wrappers `.bat`/`.cmd` com `cmd /c` antes de passar ao `subprocess.run`. CLIs Python instalados via pip/pipx no Windows criam wrappers batch que o `CreateProcess` não consegue executar diretamente.

## [0.4.0] — 2026-07-08

O flip do Python: o Koine passa a ser distribuído como aplicação Python (`koine.pyz`), substituindo os binários Go. Mesmos comandos `kn-*`, mesmo comportamento, mesmo estado em disco — upgrade da v0.3.x não exige migração.

### Added

- **Distribuição Python** — asset `koine-<versão>.zip` com `koine.pyz` (zipapp de stdlib pura — sem `.so`/`.pyd`/`.dll`) e `vault/` lado a lado. Requer Python ≥ 3.12. Sem executável compilado: nada para o antivírus bloquear além de código-fonte.
- **Comando `koine`** — wrapper administrativo (`koine versao`, `koine instalar`, `koine instalar-habilidades`, `koine gerar`, `koine mostrar`) substitui o `kn-agente`.
- **Modo interativo do `instalar`** portado por completo: prompt de pasta canônica com default `~/koine`, alias `koine`, `CONTEXTO.md` de bootstrap, detecção de harness com confirmação `[S/n]` e mensagem orientativa quando nenhum cliente IA é detectado.
- **Marker-check no working dir** — arquivo regular pré-existente SEM o marcador Koine no caminho de um artefato a gerar vai para backup `.bak` (`.bak.1`, `.bak.2`, … — nunca sobrescreve backup) com aviso de uma linha; COM marcador (ou assinatura retrocompatível das versões antigas) é regenerado silenciosamente. Paridade final com o conflito da série Go; arquivos gerados pelo Go são reconhecidos pelo Python e vice-versa.
- **Upgrade sobre instalação Go** — `koine instalar` reconhece os symlinks `kn-*` → `kn-agente` criados pela v0.3.x e os substitui pelos wrappers Python. Qualquer outro conteúdo pré-existente no caminho é preservado com aviso. `~/.config/koine/` e `~/.local/share/koine/` são lidos como estão — escopos, aliases e agentes intactos.

### Changed

- **Installers reescritos** — `install.sh`, `install.ps1` e `install.bat` agora: localizam um Python ≥ 3.12 no PATH (Unix: `python3.13`/`python3.12`/`python3`/`python`; Windows: `py -3`/`python`/`python3`), baixam `koine-<versão>.zip` da release, extraem para `~/.local/share/koine/dist/` e delegam ao `koine instalar`. Sem Python ≥ 3.12, terminam com orientação de instalação e **nada é instalado** (sem estado parcial).
- **Pipeline de release** — o CI roda a suíte Python completa (incluindo os testes de paridade, com o oráculo Go compilado do fonte do repo), valida que a versão do pacote confere com a tag e publica o pacote Python. Falha de teste bloqueia a publicação.

### Removed

- **Binários Go dos assets de release** — `kn-agente-darwin-*`, `kn-agente-linux-*` e `kn-agente-windows-*.exe` não são mais distribuídos. A série Go permanece disponível nas tags `v0.3.x`.

### Notes

- **Modo skills continua como fallback** (`koine-skills.zip`) para ambientes que bloqueiam até o interpretador Python — instalação e operação inalteradas desde a 0.3.2.
- Os caveats de assinatura/notarização das releases anteriores deixam de se aplicar: não há mais binário compilado na distribuição.

## [0.3.2] — 2026-07-07

Modo skills dual-mode: o Koine passa a operar também **sem o binário**, para ambientes que bloqueiam executáveis. Além dos binários, a release agora distribui `koine-skills.zip`.

### Added

- **Modo skills (dual-mode)** — distribuição alternativa sem binário: o Claude Code carrega o contexto Koine via skills e `@path` relativo, sem `kn-agente`. Para ambientes corporativos que bloqueiam `.exe`.
- **Skill `kn-12-prepara-contexto`** — gera o `CLAUDE.md` da pasta de trabalho e os índices de domínio sem o binário, replicando a resolução e a geração do `kn-agente`.
- **Instaladores do modo skills** — `instalar-koine.bat` (Windows: cria os diretórios XDG e copia vault + skills) e `instalar-koine.md` (guia executável por agente, com auto-teste de filesystem).
- **`koine-skills.zip` como asset de release** — montado no CI e anexado à release, ao lado dos binários.

### Changed

- **Skills `kn-01`, `kn-02`, `kn-03`, `kn-11`** — passam a contemplar o modo skills além do modo binário, qualificando a invocação por modo.

## [0.3.1] — 2026-07-02

Patch de compatibilidade. Binários recompilados com Go 1.26 para suporte a macOS 26 (Tahoe / Darwin 25).

### Fixed

- **Go 1.22 trava em macOS 26 (Darwin 25)** — o runtime Go 1.22 entra em deadlock durante inicialização em Darwin 25 antes de qualquer código de usuário rodar: sem output, sem goroutine dump no SIGQUIT. Causa raiz: mudança no scheduler de threads do macOS 26. Atualização para Go 1.26 resolve. Usuários em macOS 26 que instalaram versões anteriores devem reinstalar com `install.sh`.

## [0.3.0] — 2026-06-30

Terceira release pública. Codex CLI suportado como quinto harness e melhoria de
UX no tratamento de conflito de arquivos. Cobertura: PR #8.

### Added

- **Adapter Codex CLI (`kn-codex`)** — quinto harness suportado. Gera `AGENTS.md` com conteúdo **inline** (usuário, KOINE, agente, escopo, índices) porque o Codex injeta o texto literal do `AGENTS.md` em vez de resolver `@path` nativamente como Claude/Antigravity; o inline garante a injeção do contexto. Passa `-c project_doc_max_bytes=1048576` para não truncar bundles acima de 32 KiB. `CONTEXTO.md` permanece arquivo separado (snapshot inline + prosa apontando o arquivo mutável). Symlink `kn-codex` criado em `kn-agente instalar`; cliente listado no onboarding. PR #8.
- **Skills `kn-*` instaladas para o Codex** em `~/.agents/skills` (path USER de skills do Codex); `codex` adicionado à detecção automática de harness e a `instalar-habilidades --para=codex`. PR #8.

### Changed

- **Tratamento de conflito faz backup em vez de erro** — arquivo pré-existente não gerado pelo Koine no destino do working dir (`AGENTS.md`/`CLAUDE.md`/`GEMINI.md`) é movido para backup (`.bak`, depois `.bak.1`, `.bak.2`, … — nunca sobrescreve backup existente) e a sessão prossegue, com aviso de uma linha — em vez do erro duro que exigia `--substituir`. Vale para todos os wrappers via o resolvedor de conflito compartilhado. `--substituir` passa a significar "sobrescrever sem backup". Estados ambíguos (diretório, symlink com alvo divergente) continuam retornando erro. PR #8.

### Notes

- Caveats de assinatura permanecem da 0.2.0: binários macOS não notarizados e Windows não assinados (ver release 0.2.0 para mitigações).

## [0.2.0] — 2026-06-28

Segunda release pública. Onboarding um-comando, install scripts cross-platform,
schema CONTEXTO.md com flag `bootstrap`, skill `/kn-01-recebe-usuario` reescrita
com 4 personagens-âncora, pipeline de release automatizado. Cobertura: PRs #1
a #6 (mergeadas entre 2026-06-26 e 2026-06-28).

### Added

- **Install scripts** publicados como assets do GitHub Release: `install.sh` (Unix), `install.ps1` (Windows PowerShell), `install.bat` (Windows cmd com `-ExecutionPolicy Bypass` inline para contornar restrições corporativas). PR #4.
- **Pasta canônica em `kn-agente instalar`**: cria pasta com prompt-com-default (default `~/koine`), registra alias `koine` em `~/.config/koine/aliases.json`, gera `CONTEXTO.md` de bootstrap a partir de embed `vault/bootstrap/CONTEXTO.md`. PR #3.
- **Schema `CONTEXTO.md` com flag `bootstrap: true`** — campo opcional retrocompatível; `Resolver()` bypassa validação de escopo/dominios quando setado; emite warning se agente solicitado != Hermes. ADR `docs/decisoes/20260627-bootstrap-flag-em-contexto-md.md`. PR #3.
- **Bootstrap explícito nos 4 adapters de harness** (Claude, Antigravity, Copilot, OpenCode): carregam corpo do `CONTEXTO.md` no contexto do cliente IA quando `bootstrap: true` está presente. PR #3.
- **Pipeline de release automatizado** em `.github/workflows/release.yml`: cross-compile para `darwin-arm64`/`darwin-amd64`/`linux-amd64`/`windows-amd64`, gera `SHA256SUMS`, publica binários + scripts + checksums em GitHub Release ao push de tag `v*`. PR #2.
- **Mensagem orientativa quando zero clientes IA detectados** em `kn-agente instalar`: bloco Node.js (se ausente, com comandos por OS), bloco Homebrew (se ausente em macOS), lista dos 4 clientes IA suportados com comando de instalação por OS. PR #4.
- **Tutorial passo a passo** `docs/tutoriais/onboarding-completo.md` cobrindo do install até o primeiro agente operacional configurado, com resolução de problemas. PR #6.
- **Referência das 5 skills** em `docs/referencias/habilidades.md` com tabela compacta + sub-seções detalhadas (trigger, inputs, outputs, skills relacionadas). PR #6.
- **Dependência `golang.org/x/term`** para detecção de terminal cross-platform (PATH não atualizado, modo interativo vs CI). ADR `docs/decisoes/20260626-golang-x-term-deteccao-terminal.md`. PR #1.

### Changed

- **`/kn-01-recebe-usuario` SKILL.md reescrito** com 4 personagens-âncora (Bruce Wayne, Hermione Granger, Indiana Jones, Princesa Leia) em respostas inline lado-a-lado por pergunta — zero adaptação mental do agente. Formato padronizado: `Formato esperado`, `Como será usada`, `Se não souber`. Vocabulário pt-BR (apelido, cabeçalho, caminho, pasta padrão). Rodada 4 delega para `/kn-03-cria-agente` sem duplicar entrevista. Mensagem final usa `kn-<cliente>` dinâmico. Ao final do onboarding, reescreve `CONTEXTO.md` de bootstrap substituindo `bootstrap: true` por escopo `koine` permanente + cria `~/.config/koine/escopos/koine.md`. PR #5.
- **`kn-agente instalar` detecta harnesses no PATH** e oferece instalação de skills `kn-*` com prompt `Y/n`; aceita flag `--para=<harness>` para bypass. PR #1.
- **`harnessSuportados` expandido** para os 4 clientes IA: `claude` → `.claude/skills`, `agy` → `.gemini/antigravity-cli/skills`, `copilot` → `.copilot/skills`, `opencode` → `.config/opencode/skills`. PR #1.
- **`docs/referencias/cli.md` atualizado** com as 5 fases de `kn-agente instalar` e a distinção entre bootstrap implícito (sem CONTEXTO.md) e bootstrap explícito (com `bootstrap: true`). PR #6.

### Removed

- **`docs/tutoriais/instalacao-primeira-sessao.md`** — substituído por `onboarding-completo.md` (fluxo manual obsoleto). PR #6.

### Notes

- Binários macOS ainda não são notarizados; usuário pode ver alerta "Apple não pôde verificar" na primeira execução. Mitigação: `xattr -d com.apple.quarantine ~/.local/bin/kn-agente`.
- Binários Windows ainda não são assinados; pode disparar SmartScreen. Mitigação: comparar SHA-256 com `SHA256SUMS` publicado no release.
- Schema do `CONTEXTO.md` permanece retrocompatível: arquivos sem `bootstrap:` continuam funcionando como antes.
- Pre-release `v0.2.0-rc1` foi pulada — `v0.2.0` é o primeiro release público com binários e scripts.

## [0.1.0] — 2026-06-26

Initial public release.

### Added

- `kn-agente` administrative CLI: `instalar`, `mostrar`, `gerar`, `versao`.
- Client wrappers: `kn-claude`, `kn-agy` (Antigravity), `kn-copilot` (GitHub Copilot CLI), `kn-opencode`.
- Four-layer context model: user, agent, references, working-directory context.
- Embedded vault distributed with the binary.
- Five `kn-*` skills: catalog onboarding, catalog maintenance, agent creation,
  reference upkeep, session closure.
- XDG-compliant directories: `~/.config/koine/`, `~/.local/share/koine/`, `~/.cache/koine/`.
- Bootstrap mode for working directories without `CONTEXTO.md`.
- Cross-platform cache for Copilot and OpenCode adapters
  (`COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, `OPENCODE_CONFIG`).
- Marker-based conflict detection for files touched by adapters
  (`--substituir` flag opts in to overwrite).
- Folder resolution cascade (alias, direct path, fuzzy match with menu).

### Notes

First public release. API, on-disk layout, vault contents and adapter
behavior may evolve until 1.0.

[Unreleased]: https://github.com/jrunic/koine/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/jrunic/koine/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/jrunic/koine/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/jrunic/koine/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/jrunic/koine/releases/tag/v0.3.0
[0.2.0]: https://github.com/jrunic/koine/releases/tag/v0.2.0
[0.1.0]: https://github.com/jrunic/koine/releases/tag/v0.1.0
