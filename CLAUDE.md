# Contexto para Claude Code neste repositório

Você está trabalhando no repositório Koine — CLI Python que injeta contexto multi-camada em harnesses de IA terminal.

## Antes de fazer mudanças

- Leia `CONTEXTO.md` para stack, padrões e estrutura do código
- Para mudanças arquiteturais, leia ADRs relevantes em `docs/decisoes/`
- Para entender o produto e a forma de uso, leia `README.md`

## Convenções rápidas

- Código Python segue PEP 8; comentários em PT-BR
- Subcomandos e flags em PT-BR (exceto `--force`)
- Testes com pytest em `tests/`
- Stdlib first; dependência de runtime só vendorizada puro-Python (`src/koine/_vendor/`); nova dependência externa requer ADR
- Zero código nativo no pyz (`.pyd`/`.so`/`.dll` proibidos)
- XDG vars (`XDG_CONFIG_HOME` etc.) direto com fallback `~/.config/koine/` etc.

## Antes de commitar

```bash
.venv/bin/pytest -q
```

Tudo verde antes de qualquer commit.
