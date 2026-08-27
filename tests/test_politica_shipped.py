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


# ---- e2e: a mensagem ao usuário, que é da CLI e não da lib -------------------

import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_saida_do_instalar_cita_o_caminho_do_backup(tmp_path):
    """Critério 1 da spec: o caminho do backup é CITADO na saída. Mensagem ao
    usuário é justamente o que ninguém reexecuta à mão depois — sem esta
    asserção, o critério ficaria verificado só pela prova viva."""
    out = str(tmp_path / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"),
                    "--out", out], check=True, capture_output=True, text=True)
    pyz = os.path.join(out, "koine.pyz")
    home = str(tmp_path / "home")
    os.makedirs(home)
    env = {"HOME": home, "USERPROFILE": home, "PATH": "/usr/bin:/bin"}

    r = subprocess.run([sys.executable, pyz, "instalar"], env=env,
                       capture_output=True, text=True, timeout=90,
                       stdin=subprocess.DEVNULL)
    assert r.returncode == 0, r.stderr[-800:]

    # adultera um artefato shipped: é o estado de quem tem a versão anterior
    koine_md = os.path.join(home, ".local", "share", "koine", "KOINE.md")
    with open(koine_md, "w") as f:
        f.write("conteudo da versao anterior\n")

    r2 = subprocess.run([sys.executable, pyz, "instalar"], env=env,
                        capture_output=True, text=True, timeout=90,
                        stdin=subprocess.DEVNULL)

    assert r2.returncode == 0, r2.stderr[-800:]
    assert "sua versão anterior em" in r2.stdout
    assert os.path.join(".cache", "koine", "backups") in r2.stdout
    # e o artefato ficou novo de verdade — não só a mensagem apareceu
    assert open(koine_md).read() != "conteudo da versao anterior\n"


# ---- equivalência por célula: a raiz do problema -----------------------------

import shutil

from koine import atualizar as _atualizar
from koine import instalar as _instalar


def _estado_do_harness(home):
    """O que o usuário enxerga: nome da skill → conteúdo do SKILL.md.

    Dict, não lista de nomes: a equivalência precisa comparar CONTEÚDO. Com só
    os nomes, três harnesses com a skill em versões diferentes empatariam — a
    forma "valor igual entre ramo e fallback" aplicada ao instrumento.
    """
    base = os.path.join(home, ".claude", "skills")
    if not os.path.isdir(base):
        return {}
    return {n: open(os.path.join(base, n, "SKILL.md")).read()
            for n in sorted(os.listdir(base))
            if os.path.isfile(os.path.join(base, n, "SKILL.md"))}


def _cenario(base: pathlib.Path, monkeypatch, nome: str):
    """HOME isolado com: vault instalado na v1 e skill v1 no harness; a origem
    já avançada para v2. É o estado exato do defeito medido em produção — quem
    já usava o Koine tinha a skill anterior instalada."""
    home = base / nome
    home.mkdir()
    origem = base / f"origem-{nome}"
    d = origem / "habilidades" / "kn-99-encerra-sessao"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("skill v1")
    (origem / "KOINE.md").write_text("koine v1")

    monkeypatch.setenv("HOME", str(home))
    for k in ("XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(skills.Path, "home", staticmethod(lambda h=home: pathlib.Path(h)))

    _instalar.extrair(str(origem), "0.0.1")
    skills.instalar_habilidades_detalhado("claude", "0.0.1")
    (d / "SKILL.md").write_text("skill v2")
    (origem / "KOINE.md").write_text("koine v2")
    return home, origem


def test_os_tres_comandos_deixam_o_harness_no_mesmo_estado(tmp_path, monkeypatch):
    """As políticas divergiram porque cada comando foi testado sozinho. Este
    teste roda o MESMO cenário nos três e compara o estado resultante.

    Equivalência é POR CÉLULA: aqui, a do harness, onde os três atuam. O
    `instalar-habilidades` não toca o vault, então exigir estado idêntico em
    todas as células seria impossível — e quem escrevesse esse teste acabaria
    reduzindo a asserção até ela passar.
    """
    estados = {}

    # 1. instalar
    home, origem = _cenario(tmp_path, monkeypatch, "instalar")
    _instalar.extrair(str(origem), "0.0.2")
    skills.instalar_habilidades_detalhado("claude", "0.0.2")
    estados["instalar"] = _estado_do_harness(str(home))

    # 2. atualizar — a fase de aplicação, que é onde a política é exercida
    home, origem = _cenario(tmp_path, monkeypatch, "atualizar")
    # detectar_harnesses() varre o PATH REAL do processo: nesta máquina o
    # `claude` existe e o refresh roda; no runner do CI não existe, o harness
    # ficaria na v1 e a equivalência quebraria LÁ, com o teste certo e o
    # ambiente diferente. O seam elimina a dependência do PATH.
    monkeypatch.setattr(_atualizar.skills, "detectar_harnesses", lambda: ["claude"])
    staging = tmp_path / "staging"
    shutil.copytree(str(origem), str(staging / "vault"))
    (staging / "koine.pyz").write_text("pyz novo")
    alvo = home / "koine.pyz"
    alvo.write_text("pyz velho")
    bindir = home / "bin"
    bindir.mkdir()
    _atualizar.aplicar(str(staging), str(alvo), str(bindir), "0.0.2", force=False)
    estados["atualizar"] = _estado_do_harness(str(home))

    # 3. instalar-habilidades — o vault chega novo por outra via; só o harness
    home, origem = _cenario(tmp_path, monkeypatch, "instalar-habilidades")
    _instalar.extrair(str(origem), "0.0.2")
    skills.instalar_habilidades("claude", "0.0.2")
    estados["instalar-habilidades"] = _estado_do_harness(str(home))

    # pré-condição, NÃO redundância: sem ela, três comandos que não fizessem
    # nada passariam com estados vazios e iguais
    assert estados["instalar"] == {"kn-99-encerra-sessao": "skill v2"}, \
        "pré-condição: o cenário tem que de fato atualizar"
    assert estados["instalar"] == estados["atualizar"]
    assert estados["instalar"] == estados["instalar-habilidades"]
