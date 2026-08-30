---
descricao: Referência da configuração que o Koine escreve num orquestrador de sessões — providers, campos, matriz de clientes com caminho, e os defaults que mordem
id: 202608302010
tipo: referencia
status: ativo
tags: [referencia, koine, paseo, providers, configuracao]
---

# Referência — o Koine no orquestrador de sessões

O que a `/kn-04-conecta-o-paseo` escreve, e por quê. Para o passo a passo, veja o
[tutorial](../tutoriais/acesso-pelo-celular.md); para entender a decisão, a
[explicação](../explicacoes/por-que-paseo.md).

## A matriz, lida do próprio Koine

```
koine paseo-info          # legível
koine paseo-info --json   # para ferramenta consumir
```

Devolve, por cliente com caminho: o identificador dos dois providers, o nome do
wrapper e o tipo do provider a estender.

**Esta é a fonte.** Nenhuma cópia dela deve existir em skill, script ou anotação: ela
muda quando o Koine ganha cliente novo, e uma cópia velha produz provider que abre
sessão sem contexto e sem erro.

### Clientes com caminho

| Cliente | Tem caminho | Por quê |
|---|---|---|
| Claude Code | sim | o comando do provider é invocado por sessão, na pasta do workspace |
| GitHub Copilot CLI | sim | idem, pelo protocolo de agente |
| OpenCode | sim, **pelo protocolo genérico** | pelo tipo próprio não funciona: o gerenciador de servidor é único por processo e rejeita o comando do provider |
| Codex CLI | **não** | sobe como servidor longo, a partir da pasta de onde o serviço subiu, antes de existir workspace — nunca vê a sua pasta |
| Antigravity | **não** | não fala o protocolo de agente |

**Configurar um cliente sem caminho falha em silêncio:** o provider fica disponível,
abre sessão e responde — sem contexto nenhum.

## Wrappers

A instalação emite `kn-<cliente>-paseo` ao lado do `kn-<cliente>` que você usa no
terminal. Ele difere em três pontos:

- repassa a lista de argumentos do orquestrador intacta;
- lê o agente da variável `KOINE_AGENTE`, porque um orquestrador não passa argumento
  posicional;
- **nunca escreve na sua pasta de trabalho** — pasta ainda não configurada recebe uma
  instrução dizendo onde configurá-la.

E **nunca encerra a sessão** por estado da pasta. Por aqui não há terminal para ler
mensagem de erro nem prompt para redigitar: sessão que não abre é beco sem saída.
Três casos que no terminal são erro alto sobem, por este canal, com o Hermes
avisando — pasta sem contexto, `escopo:` que aponta para um escopo inexistente, e
agente inexistente (declarado pela pasta ou pedido pelo provider). Em todos, o
`CONTEXTO.md` fica intacto e o aviso traz o nome exato do que não foi encontrado.

`koine atualizar` regenera os wrappers, então quem já tem instalado os recebe sem
reinstalar.

## Os dois providers por cliente

| Identificador | Diferença |
|---|---|
| `kn-<cliente>` | genérico — a pasta decide o agente |
| `kn-<cliente>-hermes` | força o Hermes por `KOINE_AGENTE`, mesmo em pasta cujo padrão é outro |

Os identificadores são **prescritos pelo Koine**, não escolhidos por quem configura.
Nome inventado diverge entre máquinas, e ferramenta que um dia precise ler ou
consertar essa configuração encontraria dois vocabulários para a mesma coisa.

### O comando vai por caminho absoluto

O serviço do orquestrador roda com ambiente mínimo, e a pasta de programas do seu
usuário **não** está no caminho de busca dele. Com o nome puro, o provider fica
indisponível com "caminho não resolvido", e a sessão não sobe.

```
command -v kn-claude-paseo      # macOS e Linux
where kn-claude-paseo           # Windows
```

## Três defaults que mordem

São os pontos onde o comportamento observado difere do que se espera — os três foram
medidos, e os três produzem falha silenciosa ou pior.

### 1. Omitir a chave de relay expõe a máquina

A documentação do produto diz que o relay fica desabilitado por padrão. **Num arquivo
de configuração escrito à mão, o oposto acontece:**

| `daemon.relay` | resultado |
|---|---|
| ausente | conecta ao relay — a máquina fica alcançável pela internet |
| `{"enabled": false}` | não conecta |

Escrever `false` não é redundância. Quem liga o relay é você, na tela do aplicativo,
depois de decidir.

### 2. O comando cai na porta padrão

A ajuda do próprio comando diz: *"default: local socket/pipe, then localhost:6767"*.
Numa máquina com **duas pessoas** usando o orquestrador, isso significa que — com o
seu serviço parado — um comando seu de listar ou de parar **acerta o serviço da outra
pessoa**.

Onde a porta não for a padrão, fixe a escolha:

```
export PASEO_HOST=127.0.0.1:<sua porta>
```

E escolha a porta **no arquivo de configuração** (`daemon.listen`), nunca por
argumento ou variável de ambiente: os dois deixam a tela do aplicativo mostrando um
valor sem efeito, em silêncio.

### 3. A pasta de configuração é identidade e registro

Ela guarda o par de chaves e o identificador que os aparelhos pareados conhecem — e
também o registro de projetos e workspaces.

Movê-la ou apagá-la faz o serviço renascer com identidade nova: **todo celular
pareado deixa de encontrá-lo**, e o sintoma é tempo esgotado sem mensagem de erro.
Mover, nunca apagar; e para recuperar um pareamento perdido, devolver os dois
arquivos de identidade da cópia antiga.

## Ditado

O modelo de ditado é escolhido no arquivo de configuração, e a ordem importa: os
modelos são baixados **quando o serviço sobe**, e ele sobe quando o aplicativo abre.

| Modelo | Idiomas |
|---|---|
| padrão de fábrica | inglês apenas |
| o que o Koine escreve | 25 idiomas europeus, com detecção automática |

Não há ajuste por idioma para o modelo local — a detecção é automática. O campo
`language` que aparece na documentação do produto vale **só** para o provedor pago.

Trocar de modelo depois **baixa outro**, não substitui. Configurar antes da primeira
abertura é a diferença entre um download e três.

O Koine também deixa o modo de voz desligado, o que evita baixar um modelo de fala
que só existe em inglês. Para as duas pontas em português, veja
[voz com serviço pago](../guias/voz-com-openai.md).

## Projetos e workspaces

Duas camadas: o **projeto** aponta para a pasta e agrupa; o **workspace** pendura
nele. A `/kn-14-organiza-workspaces` resolve as duas.

São **três comandos** por pasta, não um:

- criar projeto **não aceita nome** — ele sai do nome da pasta, e o nome humano exige
  um segundo comando;
- criar projeto **não cria workspace**.

`isolation: local` é o padrão correto — o agente trabalha na pasta real. Pasta que não
é repositório git aceita **só** essa forma.

Se você abrir uma pasta não registrada, o orquestrador cria o registro sozinho — com
o nome da pasta e sem escolher agrupamento. A skill existe para você decidir a
organização, não para destravar o uso.
