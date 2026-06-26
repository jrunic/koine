# Contexto para Claude Code neste repositório

Você está trabalhando no repositório Koine — CLI Go que injeta contexto multi-camada em harnesses de IA terminal.

## Antes de fazer mudanças

- Leia `CONTEXTO.md` para stack, padrões e estrutura do código
- Para mudanças arquiteturais, leia ADRs relevantes em `docs/decisoes/`
- Para entender o produto e a forma de uso, leia `README.md`

## Convenções rápidas

- Código em inglês (Go); comentários em PT-BR
- Subcomandos e flags em PT-BR (exceto `--force`)
- Testes com stdlib `testing` — sem testify, gomock ou similares
- Stdlib first; nova dependência externa requer ADR
- `os.UserConfigDir`/`os.UserCacheDir` proibidos — usar `XDG_CONFIG_HOME` / `XDG_CACHE_HOME` direto com fallback `~/.config/koine/` etc.

## Antes de commitar

```bash
go fmt ./... && go vet ./... && go build ./... && go test ./...
```

Tudo verde antes de qualquer commit.
