import os
import pathlib

from koine import paths, skills


def _vault_com_skill(tmp_path, texto):
    vault = tmp_path / "vault"
    d = vault / "habilidades" / "kn-99-encerra-sessao"
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(texto)
    return vault


def _ambiente(tmp_path, monkeypatch, texto):
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    monkeypatch.setenv("HOME", str(home))
    for k in ("XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME"):
        monkeypatch.delenv(k, raising=False)
    vault = _vault_com_skill(tmp_path, texto)
    monkeypatch.setattr(paths, "vault_dir", lambda: str(vault))
    monkeypatch.setattr(skills.Path, "home", staticmethod(lambda: pathlib.Path(home)))
    return vault


def _skills_do_harness(tmp_path):
    d = tmp_path / "home" / ".claude" / "skills"
    return sorted(os.listdir(d)) if d.is_dir() else []


def test_skill_divergente_no_harness_atualiza_e_guarda(tmp_path, monkeypatch):
    vault = _ambiente(tmp_path, monkeypatch, "skill v1")
    skills.instalar_habilidades_detalhado("claude", "0.0.1")
    (vault / "habilidades" / "kn-99-encerra-sessao" / "SKILL.md").write_text("skill v2")

    criadas, existentes, atualizadas = skills.instalar_habilidades_detalhado("claude", "0.0.2")

    instalada = tmp_path / "home" / ".claude" / "skills" / "kn-99-encerra-sessao" / "SKILL.md"
    # 1. ficou nova
    assert instalada.read_text() == "skill v2"
    # 2. e a anterior é recuperável — asserção separada
    assert len(atualizadas) == 1
    nome, bak = atualizadas[0]
    assert nome == "kn-99-encerra-sessao"
    assert open(os.path.join(bak, "SKILL.md")).read() == "skill v1"


def test_backup_nao_vira_skill_instalada(tmp_path, monkeypatch):
    """A guarda do achado da sabatina: backup gravado onde algo enumera vira
    artefato. Mede pelo que o usuário ENXERGA — a lista de skills —, não pela
    ausência de um sufixo específico, que voltaria com outro nome."""
    vault = _ambiente(tmp_path, monkeypatch, "skill v1")
    skills.instalar_habilidades_detalhado("claude", "0.0.1")
    antes = _skills_do_harness(tmp_path)
    (vault / "habilidades" / "kn-99-encerra-sessao" / "SKILL.md").write_text("skill v2")

    skills.instalar_habilidades_detalhado("claude", "0.0.2")

    assert _skills_do_harness(tmp_path) == antes
    assert antes == ["kn-99-encerra-sessao"]


def test_segunda_rodada_e_no_op_e_o_comando_rodou(tmp_path, monkeypatch):
    """Ausência de mudança sem prova de execução mede o mesmo que um comando
    inexistente mediria — daí a asserção sobre `existentes`."""
    _ambiente(tmp_path, monkeypatch, "skill v1")
    skills.instalar_habilidades_detalhado("claude", "0.0.1")

    criadas, existentes, atualizadas = skills.instalar_habilidades_detalhado("claude", "0.0.1")

    assert atualizadas == []
    assert criadas == []
    assert existentes == ["kn-99-encerra-sessao"]   # prova de que rodou
