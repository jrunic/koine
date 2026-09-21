---
descricao: Guia para quem usa Koine — por que uma sessão pelo Paseo às vezes abre com Hermes em vez do seu agente do dia a dia, e como corrigir cada causa
id: 202609211500
tipo: guia
status: ativo
projeto: koine
escopo: repo:koine
plataforma: "*"
dominios: [tecnologia]
tags: [guia, koine, paseo, agente, definir-agente, celular]
---

# Guia — Corrigir agente errado no Paseo

Audiência: quem abre sessão pelo celular (ou por qualquer provider genérico do
Paseo) e recebe **Hermes** em vez do agente que usa no dia a dia.

Não é bug de sessão específica — é sempre a mesma causa: **a pasta que você
abriu não diz qual agente usar, e o seu usuário também não tem um default
gravado.** Este guia mostra como diagnosticar e como corrigir, por cenário.

## O sintoma

Você abre uma sessão pelo celular (ou digita `kn-claude <pasta>` no terminal,
sem nome de agente) e quem responde é o Hermes — o agente de configurar o
Koine, não o seu agente operacional. A sessão funciona, carrega contexto, só
não é quem você esperava.

## Por que isso acontece

Toda sessão resolve o agente por uma cadeia de precedência, do mais
específico ao mais genérico:

1. **Nome digitado na hora** — `kn-claude leia <pasta>`. Só vale naquela
   sessão; não fica gravado em lugar nenhum.
2. **Campo da pasta** — `agente:` no `CONTEXTO.md` daquela pasta específica.
3. **Seu default** — `agente-default:` no seu arquivo de usuário.
4. **`hermes`** — se nada dos três acima existir.

O provider genérico do Paseo (`kn-<cliente>`, sem `-hermes` no nome) **não
tem como passar o passo 1** — um orquestrador não digita nada por você. Ele
sempre cai direto no passo 2, e se a pasta não declarar agente próprio, no 3.
**Se o seu default nunca foi gravado, não sobra nada além do 4.** É por isso
que o sintoma aparece mais forte no Paseo do que no terminal: no terminal
você digitava o nome todo dia sem perceber que estava suprindo, sozinho, o
que faltava configurar.

## Diagnóstico — descubra qual cenário é o seu

```
koine paseo-doctor
```

Ou, se você nem usa Paseo:

```
koine validar
```

Os dois leem a mesma verificação e apontam um dos quatro cenários abaixo.

## Cenário 1 — você tem 1 agente e nunca gravou o default

É o mais comum, e não é falha sua: `koine definir-agente --default` e a regra
"primeiro agente vira default automático" só existem desde 28/08/2026. Quem
criou o único agente antes dessa data nunca teve a chance de ganhar isso de
graça.

**A partir desta versão, o Koine corrige sozinho.** Rode:

```
koine atualizar
```

ou, se já está na versão mais recente:

```
koine instalar
```

Os dois imprimem uma linha quando gravam:

```
✓ agente-default: <nome> (o único agente que você tem — gravado automaticamente)
```

Se você está numa versão anterior a essa correção, ou prefere não esperar
pelo `atualizar`, o comando manual é:

```
koine definir-agente <nome> --default
```

## Cenário 2 — você tem 2 ou mais agentes e nenhum default

Aqui o Koine **não adivinha** — não há como saber qual dos seus agentes é o
"principal". `koine paseo-doctor` e `koine validar` avisam, mas não corrigem
sozinhos. Escolha o que você mais usa e grave:

```
koine definir-agente <nome> --default
```

Isso não muda o comportamento das pastas que já declaram o próprio
`agente:` — o passo 2 da cadeia continua vencendo o passo 3. O default só
entra nas pastas que não têm nada próprio configurado.

## Cenário 3 — o default aponta para um agente que não existe mais

Sintoma: o diagnóstico avisa que `agente-default` referencia um nome sem
arquivo correspondente em `~/.config/koine/agentes/`. Normalmente é agente
renomeado ou apagado manualmente.

O Koine também não corrige este sozinho — sobrescrever o valor exigiria
adivinhar a intenção. Regrave para o nome certo:

```
koine definir-agente <nome-correto> --default
```

## Cenário 4 — uma pasta específica deveria abrir com outro agente

Diferente dos três cenários acima: aqui o seu default está certo, mas **uma
pasta em particular** precisa de um agente diferente do seu dia a dia — por
exemplo, uma pasta de um projeto que só um agente específico atende.

```
koine definir-agente <nome> <pasta>
```

Isso grava `agente:` no `CONTEXTO.md` daquela pasta — vence o default (passo
2 antes do passo 3), só para ali.

## Depois de corrigir

Não precisa reabrir o app nem re-parear o celular — o Koine lê o `agente:`/
`agente-default:` a cada sessão nova, não em cache. A próxima sessão que você
abrir naquela pasta (ou em qualquer pasta sem `agente:` próprio, se foi o
default que você corrigiu) já chega com o agente certo.

Se ainda vier Hermes depois de corrigir, confira com `koine paseo-info` se o
provider que você abriu é mesmo o `kn-<cliente>` genérico — o provider
`kn-<cliente>-hermes` **força** Hermes por desenho, independente de qualquer
default, e é para isso que ele existe.

## Se você organiza muitas pastas de uma vez (`/kn-14-organiza-workspaces`)

Registrar 10, 20, 30 pastas de uma sessão só multiplica o efeito do cenário
1 ou 2: nenhuma delas declara `agente:` próprio a menos que você peça, então
todas dependem do seu default para não caírem em Hermes. A
`/kn-14-organiza-workspaces` roda `koine paseo-doctor` ao final exatamente
por isso — confira o aviso ali antes de considerar o trabalho terminado.

## Referências

- [Referência — o Koine no orquestrador de sessões](../referencias/paseo.md) — a
  matriz de providers e os defaults que mordem
- [Referência — comandos do CLI](../referencias/cli.md) — `koine definir-agente`,
  `koine validar`, `koine paseo-doctor`
- [Guia — abrir sessões Koine de fora do computador](acesso-remoto.md)
