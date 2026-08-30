---
name: kn-14-organiza-workspaces
description: Registra suas pastas de trabalho no Paseo, para abri-las de fora do computador. Varre o que você tem, propõe uma organização e cria projeto e workspace com o nome certo — resolvendo as duas camadas que a interface do Paseo expõe cruas. Rode toda vez que nascer pasta de trabalho nova. Precisa da /kn-04-conecta-o-paseo feita antes.
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
