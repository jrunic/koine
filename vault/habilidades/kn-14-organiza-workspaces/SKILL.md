---
name: kn-14-organiza-workspaces
description: Registra pastas de trabalho no Paseo para abri-las de fora. Cria projeto e workspace, renomeia o título, arquiva. Avisa: mv na pasta com o daemon no ar arquiva sozinho; não há mover entre projetos. Precisa da /kn-04 feita antes.
id: 202608301720
projeto: koine
tipo: habilidade
status: ativo
tags: [habilidade, koine, paseo, workspaces, projetos, cotidiano]
---

# kn-14 — Organiza projetos e workspaces

Registra as pastas de trabalho do usuário no Paseo, para ele abri-las do celular.

**Se o Paseo ainda não está configurado nesta máquina**, pare e mande rodar a
`/kn-04-conecta-o-paseo` primeiro — sem ela não há onde registrar. Para saber:

```
paseo status
```

Se não responder, é a `/kn-04` que falta.

**Se houver mais de uma pessoa usando o Paseo nesta máquina**, confirme que você está
falando com o serviço certo antes de criar qualquer coisa: `paseo status` mostra o
campo `Home`, que precisa ser o do usuário atual. O comando **cai na porta padrão**
quando não acha o serviço configurado — e criaria projeto no registro de outra
pessoa, sem avisar.

**Diga também o que ele NÃO precisa fazer:** não é preciso rodar esta skill antes de
cada sessão. Se ele abrir uma pasta que não está registrada, o Paseo se vira e cria o
registro sozinho — só que com o nome da pasta e sem escolher onde agrupar. Esta skill
existe para ele **decidir a organização**, não para destravar o uso. Sem isso o
usuário passa a achar que precisa de uma etapa antes de cada trabalho, e desiste.

---

## 1. O que ele tem

Pergunte quais pastas ele quer alcançar de fora. Se não souber listar, procure no
computador dele pastas que tenham `CONTEXTO.md` e mostre o que achou.

**Confira cada uma antes de propor.** Pasta cujo `CONTEXTO.md` não declara escopo não
deve virar workspace: ela subiria **sem o contexto dele**, que é exatamente o
problema que estamos evitando. Para essas, mande rodar `/kn-02-mantem-catalogo` no
Fluxo 3 primeiro, e siga com as outras.

## 2. A organização

Projeto agrupa; workspace é a pasta dentro dele.

Proponha o agrupamento a partir do que viu — o escopo de cada pasta costuma ser uma
boa divisão — e **mostre a proposta antes de criar qualquer coisa**. É a única decisão
que é do usuário aqui; o resto é mecânica.

---

## 3. Criar

Para cada pasta são **três** comandos, não um:

```
paseo project create <caminho da pasta>
paseo project rename <id do projeto> "<nome humano>"
paseo workspace create --isolation local --path <caminho> --project <id> --title "<título>"
```

Por que três:

- **criar projeto não aceita nome.** Ele sai do nome da pasta — um projeto na pasta
  `instalar-paseo` nasce chamado `instalar-paseo`. O nome humano exige o segundo
  comando.
- **criar projeto não cria workspace.** São camadas separadas, e o comando de uma não
  toca a outra.

`--isolation local` é o que ele quer: o agente trabalha na pasta de verdade. Pasta que
não é repositório git **só** aceita essa forma.

### Se já existe

Antes de criar, liste:

```
paseo project ls
paseo workspace ls
```

Três estados possíveis, e **o do meio é o que mais acontece** — é a execução anterior
que parou entre os comandos:

| estado | o que fazer |
|---|---|
| nada existe | os três comandos |
| projeto existe, **sem workspace** | **não crie outro projeto** — renomeie se o nome ainda for o da pasta, e crie só o workspace |
| os dois existem | não faça nada, e diga que já estava certo |

## 4. Conferir

```
paseo workspace ls
```

Cada pasta aparecendo com o título combinado. Diga ao usuário que elas já estão
visíveis no celular — não é preciso fazer mais nada no aparelho.

## 5. Mudar o título visível

Isso **não** muda o caminho da pasta. O Paseo indexa estado pelo cwd.

```
paseo workspace rename <id> "<título>"
paseo workspace rename <id> --reset
```

`--reset` volta ao nome da pasta ou da branch. Para achar o id: `paseo workspace ls`.

Título de **projeto** continua `paseo project rename` (seção 3). Não rode estes comandos de dentro da sessão **daquele** workspace.

## 6. Arquivar

```
paseo workspace archive <id>
```

O workspace sai da lista ativa. Esta CLI **não tem** `unarchive` — não tem como desarquivar. Não promete devolver transcript do cliente. Não arquive de dentro da sessão daquele workspace.

## 7. Não se move entre projetos

Não existe verbo de mover workspace. `--project` só vale na criação.

Arquivar e recriar no outro projeto **perde** o estado indexado pelo caminho. Esta skill **não faz isso**. Deixe no projeto atual, ou o usuário aceita a perda por conta própria.

## 8. Não dê mv na pasta com o daemon no ar

Medido: o daemon **auto-arquiva** o workspace em segundos. A sessão órfã. Nome visível = seção 5, não `mv`.
