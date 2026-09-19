---
id: 202609191700
tipo: decisao
status: aprovado
projeto: koine
escopo: repo:koine
plataforma: "*"
dominios: [tecnologia]
description: "ADR — o relato de erro do mentorado vai para repositório privado dedicado, publicado por serviço intermediário em contabo, nunca por credencial embutida no .pyz"
tags: [adr, koine, suporte, relato, seguranca]
---

# ADR — Relato de erro do mentorado passa por serviço intermediário, nunca por token embutido

## Status

Aceito.

## Contexto

Mentorados sem experiência técnica não têm como diagnosticar sozinhos um erro que o
Koine ainda não resolve em código. O canal informal usado até aqui (WhatsApp, print,
e-mail) já mostrou falhar: a coleta de diagnóstico pediu ao mentorado rodar um prompt
de diagnóstico e ele bateu no mesmo bug que deveria diagnosticar (caso do
`kn-opencode`, 16/09/2026), e o retorno depende do mantenedor estar disponível na
hora certa.

A skill `kn-17-trata-erro` (a especificar) vai, quando não resolver sozinha consultando
`docs/referencias/erros-conhecidos.md`, montar um **relato** e pedir confirmação ao
mentorado antes de enviá-lo. Esse relato carrega, por natureza, dado de negócio do
mentorado — nome de pasta de trabalho, nome de workspace, cliente do cliente — visto em
produção num diagnóstico real, com caminho absoluto contendo nome de empresa e
workspaces nomeados por conta real do mentorado. Isso descarta publicar o relato no
repositório público do Koine.

## Decisão

O relato vai para um **repositório GitHub privado, dedicado** — separado do repositório
público do produto. A publicação nunca acontece por credencial embutida no `.pyz`
distribuído: passa por um **serviço intermediário**, hospedado em `contabo`, que guarda
a credencial de escrita e expõe um endpoint HTTP simples, chamado por `curl` (universal,
inclusive nas máquinas mais travadas medidas até aqui). O agente do mentorado nunca fala
com a API do GitHub diretamente, e nunca detém credencial de escrita.

## Alternativas consideradas

- **Token de escrita embutido no `.pyz`** — rejeitada. O modelo de permissão do GitHub
  não distingue "escrever" de "ler": um fine-grained PAT ou instalação de GitHub App com
  permissão de Issues concede leitura junto com a escrita. Embutir esse token num
  artefato público — o `.pyz` é Python legível, baixável por qualquer um — dá a qualquer
  pessoa leitura de **todos** os relatos privados de **todos** os mentorados. Um repo
  privado com esse token embutido é pior que assumir o repo como público, porque cria
  falsa sensação de proteção.
- **Relato por e-mail** — rejeitada como transporte de entrada: nem todo agente/cliente
  sabe enviar e-mail. Fica reservada como possível notificação de saída no futuro, ao
  lado da notificação nativa do GitHub.
- **Mentorado como colaborador individual do repo privado (papel "Triage")** — evitaria
  credencial e serviço próprio, mas exige que cada mentorado tenha ou crie conta GitHub e
  autorize `gh`/navegador antes do primeiro relato. Rejeitada por ora: prioriza-se menos
  fricção para o mentorado, aceitando o custo de manter um serviço próprio.

## Consequências

- Nasce um serviço novo na frota, pelo padrão `ops-04-deploy-servico`, no host
  `contabo`, com credencial guardada via `jd-secrets`.
- O agente do mentorado nunca detém credencial de escrita no GitHub para este fluxo —
  reduz a zero a superfície de vazamento do lado do cliente.
- Fica pendente medir empiricamente, antes de implementar o serviço, que "escrita
  implica leitura" vale mesmo no modelo de permissão do GitHub (fine-grained PAT e
  GitHub App) — ponto nomeado, não bloqueante para esta decisão.
- O corpo do relato passa por redação automática (caminho absoluto truncado logo abaixo
  de `$HOME`; nome da pasta de trabalho nunca incluído) e por confirmação resumida do
  mentorado antes do envio — a decisão aqui cobre só o transporte e a custódia da
  credencial, não a política de conteúdo, que fica com a spec da skill.

## Referências

- Skill `kn-17-trata-erro` (a especificar) — aciona o relato quando a consulta a
  `docs/referencias/erros-conhecidos.md` não resolve o erro.
- Sabatina de 19/09/2026 em `13-processos/manter-koine/` — decisões completas do
  desenho (repositório privado, redação, dedup, notificação, localização do doc de
  erros conhecidos).
