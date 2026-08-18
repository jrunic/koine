"""Invariantes das skills do vault.

O contrato não é nosso: o opencode só reconhece uma skill se o `name` do
frontmatter casar o nome do diretório que contém o SKILL.md, e recusa
`description` fora de 1..1024 caracteres. Skill que viola isso não dá erro —
some da lista de skills disponíveis, o que é bem pior de diagnosticar.
Referência: https://opencode.ai/docs/skills

Guarda o vault inteiro, não só a skill do dia: o custo de manter é zero e o
defeito que ela pega é silencioso em produção.
"""
import os

import pytest

from koine import frontmatter

HABILIDADES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vault", "habilidades")

# regex de nome do opencode: ^[a-z0-9]+(-[a-z0-9]+)*$
import re

NOME_VALIDO = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _skills():
    return sorted(d for d in os.listdir(HABILIDADES)
                  if os.path.isdir(os.path.join(HABILIDADES, d)))


def test_vault_tem_skills():
    """Sanity: a coleta acima não pode passar por vacuidade."""
    assert len(_skills()) >= 10


@pytest.mark.parametrize("skill", _skills())
def test_skill_declara_name_igual_ao_diretorio(skill):
    fm, _ = frontmatter.ler_arquivo(os.path.join(HABILIDADES, skill, "SKILL.md"))
    assert fm.get("name") == skill, (
        f"{skill}: name={fm.get('name')!r} não casa o diretório — o opencode "
        "descarta a skill em silêncio")


@pytest.mark.parametrize("skill", _skills())
def test_skill_tem_nome_na_forma_aceita(skill):
    assert NOME_VALIDO.match(skill), f"{skill}: fora de ^[a-z0-9]+(-[a-z0-9]+)*$"


@pytest.mark.parametrize("skill", _skills())
def test_skill_tem_description_dentro_do_limite(skill):
    fm, _ = frontmatter.ler_arquivo(os.path.join(HABILIDADES, skill, "SKILL.md"))
    desc = fm.get("description") or ""
    assert 1 <= len(desc) <= 1024, f"{skill}: description com {len(desc)} caracteres"
