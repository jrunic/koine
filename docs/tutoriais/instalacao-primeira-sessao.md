---
descricao: Tutorial passo a passo — do binário baixado até a primeira sessão funcionando
id: 202606261000
tipo: tutorial
status: ativo
tags: [tutorial, instalacao, primeira-sessao]
---

# Tutorial — Instalação e primeira sessão

Este tutorial leva você do zero até uma sessão de IA funcionando com Koine em ~5 minutos. Pré-requisito: ter um dos clientes IA suportados instalado e funcionando antes (`claude`, `agy`, `copilot` ou `opencode`).

## 1. Instalar o binário

```bash
# macOS Apple Silicon — exemplo
curl -L https://github.com/jrunic/koine/releases/latest/download/kn-agente-darwin-arm64 -o /usr/local/bin/kn-agente
chmod +x /usr/local/bin/kn-agente
```

Verifique:

```bash
kn-agente --versao
# Esperado: kn-agente 0.1.0
```

## 2. Extrair vault e criar symlinks de cliente

```bash
kn-agente instalar
```

O comando:

- Cria `~/.local/share/koine/` com `KOINE.md`, agente Hermes, skills e templates (readonly em runtime).
- Cria `~/.config/koine/dominios/` com 4 domínios canônicos.
- Cria symlinks `kn-claude`, `kn-agy`, `kn-copilot`, `kn-opencode` no mesmo diretório de `kn-agente`.

Verifique:

```bash
which kn-claude
# Esperado: /usr/local/bin/kn-claude (symlink → kn-agente)

ls ~/.local/share/koine/
# Esperado: KOINE.md, agentes/, habilidades/, templates/, .meta.json
```

## 3. Criar seu arquivo de usuário

Crie `~/.config/koine/<seu-primeiro-nome>.md` com perfil mínimo:

```bash
mkdir -p ~/.config/koine
cat > ~/.config/koine/<seu-nome>.md <<'EOF'
---
type: Profile
title: <Seu Nome Completo>
timezone: America/Sao_Paulo
idioma: pt-BR
---

# <Seu Nome>

Estilo de comunicação: direto, técnico, sem rodeios.

Background curto: <2-3 frases sobre você profissionalmente>.
EOF
```

## 4. Criar a primeira pasta de trabalho com CONTEXTO.md

```bash
mkdir -p ~/projeto-piloto && cd ~/projeto-piloto
cat > CONTEXTO.md <<'EOF'
---
escopo: piloto
dominios: [universal, tecnologia]
---

# Projeto piloto

Pasta de teste do Koine.
EOF
```

## 5. Abrir o cliente IA com contexto Koine

```bash
kn-claude hermes .
```

O que acontece nos bastidores:

1. `kn-claude` resolve a pasta (`.` → `~/projeto-piloto`).
2. Lê `CONTEXTO.md`; identifica escopo `piloto` e domínios `[universal, tecnologia]`.
3. Gera `~/projeto-piloto/CLAUDE.md` com referências `@/` para arquivo do usuário, KOINE.md, Hermes, escopo, índices de domínio e `CONTEXTO.md` local.
4. Lança `claude` na pasta.

Pergunte ao Hermes: *"Qual é o meu nome?"* Ele deve responder com o nome do arquivo do usuário.

## 6. Próximos passos

- Catalogar uma referência: `/kn-11-mantem-referencia` dentro da sessão.
- Criar um agente operacional especializado: `/kn-03-cria-agente`.
- Encerrar a sessão com diário: `/kn-99-encerra-sessao`.

Para entender o modelo de quatro camadas, ver [explicação](../explicacoes/quatro-camadas.md). Para o schema completo do `CONTEXTO.md`, ver [referência](../referencias/contexto-md.md).
