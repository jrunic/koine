# Changelog

All notable changes to Koine are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/jrunic/koine/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jrunic/koine/releases/tag/v0.1.0
