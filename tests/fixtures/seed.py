import os
import shutil

REPO = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

USUARIO = """---
type: usuario
nome: Teste
idioma: pt-BR
timezone: America/Cuiaba
---

# Teste

Usuário de fixture.
"""

ESCOPO = """---
type: escopo
nome: fixture
pasta-referencias: home:refs-fixture
---

# fixture
"""

DOMINIO_TEC = """---
type: dominio
title: Tecnologia
sinopse: Conhecimento técnico reutilizável — código, infra, ferramentas.
---

# Tecnologia

Corpo denso do domínio (não vai pro índice).
"""

# frontmatter OKF EXÓTICO de propósito: asterisco com aspas, ':' no valor
REF_A = """---
type: referencia
title: "Ref A"
description: "Nota com dois-pontos: exemplo e travessão — real"
dominios: [tecnologia]
plataforma: "*"
---

# Ref A
"""

REF_B = """---
type: referencia
title: Ref B
description: Segunda referência do escopo
dominios: [tecnologia]
---

# Ref B
"""

CONTEXTO = """---
type: contexto
escopo: fixture
dominios: [tecnologia]
---

# Pasta de trabalho de teste
"""


def montar(base: str) -> dict:
    """Cria HOME isolado em `base`. Devolve paths úteis."""
    home = os.path.join(base, "home")
    cfg = os.path.join(home, ".config", "koine")
    data = os.path.join(home, ".local", "share", "koine")
    refs = os.path.join(home, "refs-fixture")
    trab = os.path.join(home, "trabalho")
    for d in (cfg, os.path.join(cfg, "escopos"), os.path.join(cfg, "dominios"),
              data, os.path.join(data, "agentes"), refs, trab):
        os.makedirs(d, exist_ok=True)

    _w(os.path.join(cfg, "teste.md"), USUARIO)
    _w(os.path.join(cfg, "escopos", "fixture.md"), ESCOPO)
    _w(os.path.join(cfg, "dominios", "tecnologia.md"), DOMINIO_TEC)
    # KOINE.md e hermes.md vêm do vault real do repo (mesmos bytes distribuídos)
    shutil.copy(os.path.join(REPO, "vault", "KOINE.md"),
                os.path.join(data, "KOINE.md"))
    shutil.copy(os.path.join(REPO, "vault", "agentes", "hermes.md"),
                os.path.join(data, "agentes", "hermes.md"))
    _w(os.path.join(refs, "ref-a.md"), REF_A)
    _w(os.path.join(refs, "ref-b.md"), REF_B)
    _w(os.path.join(trab, "CONTEXTO.md"), CONTEXTO)

    return {"home": home, "cfg": cfg, "data": data, "refs": refs, "trab": trab}


def semear_trabalho(home: str) -> str:
    """Semeia arquivo do usuário + escopo + refs + pasta de trabalho num HOME
    onde o `koine instalar` JÁ rodou. NÃO planta dominios/KOINE/hermes — usa os
    REAIS do vault instalado. As refs declaram o domínio 'tecnologia' (existe no
    vault real). Devolve o path da pasta de trabalho. Evita o montar+cirurgia."""
    cfg = os.path.join(home, ".config", "koine")
    refs = os.path.join(home, "refs-fixture")
    trab = os.path.join(home, "trabalho")
    for d in (os.path.join(cfg, "escopos"), refs, trab):
        os.makedirs(d, exist_ok=True)
    _w(os.path.join(cfg, "teste.md"), USUARIO)
    _w(os.path.join(cfg, "escopos", "fixture.md"), ESCOPO)
    _w(os.path.join(refs, "ref-a.md"), REF_A)
    _w(os.path.join(refs, "ref-b.md"), REF_B)
    _w(os.path.join(trab, "CONTEXTO.md"), CONTEXTO)
    return trab


def _w(path: str, conteudo: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(conteudo)
