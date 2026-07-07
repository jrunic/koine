# Instalar Koine (modo skills) — guia passo a passo

Este guia instala o Koine **sem o executável**. Dois usos:

- **Humano:** siga os passos manualmente.
- **Agente:** se o `instalar-koine.bat` não rodou, abra o `claude` nesta pasta (`~/koine`) e diga: *"Execute o instalar-koine.md"*. O agente segue as instruções abaixo.

## Instruções para o agente

Você vai copiar arquivos do payload `.koine-bootstrap/` (ao lado deste guia) para os diretórios do Koine. **Antes de copiar, teste o que você consegue fazer neste sistema de arquivos e me reporte.**

### Passo 0 — Auto-teste de capacidades (obrigatório, antes de tocar em qualquer coisa)

Descubra o HOME (`echo $HOME` no Unix, `echo %USERPROFILE%` no Windows). Então sonde, **nesta ordem**, reportando o resultado de cada:

1. **Criar diretório:** tente criar `HOME/.local/share/koine/` e `HOME/.config/koine/` e `HOME/.claude/skills/`. Funcionou?
2. **Copiar arquivo:** copie um arquivo pequeno do payload para o destino de teste. Funcionou?
3. **Symlink (preferível, se permitido):** tente criar um symlink de uma skill do payload para `HOME/.claude/skills/`. Funcionou ou o sistema barrou?

Reporte uma tabela: capacidade → ok/barrado. **Escolha a estratégia:** se symlink funciona, use symlink para as skills (economiza espaço, atualiza junto com o payload); se barrado, use cópia. Para o resto (KOINE.md, agentes, conceitos, dominios), sempre cópia.

Se **criar diretório** ou **copiar** falharem, pare e reporte — sem isso, o modo skills não instala; escale para a TI.

### Passo 1 — Criar diretórios

- `HOME/.local/share/koine/` (com `agentes/`, `conceitos/`)
- `HOME/.config/koine/` (com `dominios/`, `escopos/`, `agentes/`)
- `HOME/.claude/skills/`

### Passo 2 — Copiar o conteúdo do vault (do payload `.koine-bootstrap/`)

- `.koine-bootstrap/KOINE.md` → `HOME/.local/share/koine/KOINE.md`
- `.koine-bootstrap/agentes/` → `HOME/.local/share/koine/agentes/`
- `.koine-bootstrap/conceitos/` → `HOME/.local/share/koine/conceitos/`
- `.koine-bootstrap/dominios/` → `HOME/.config/koine/dominios/`

### Passo 3 — Instalar as skills

- Para cada pasta `.koine-bootstrap/habilidades/kn-*` → `HOME/.claude/skills/kn-*` (symlink se o auto-teste permitiu; senão cópia).

### Passo 4 — Verificar e reportar

Confirme que existem: `HOME/.local/share/koine/KOINE.md`, `.../agentes/hermes.md`, `.../conceitos/escopos.md`, `HOME/.config/koine/dominios/universal.md`, `HOME/.claude/skills/kn-01-recebe-usuario`. Reporte cada um. Ao final, diga ao usuário:

> Instalação concluída. Feche esta sessão, e abra o Claude Code aqui em `~/koine` — o Hermes inicia o onboarding automaticamente.
