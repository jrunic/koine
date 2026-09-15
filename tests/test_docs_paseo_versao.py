"""Cinco docs de Paseo declaram versão e data (jd-task #885)."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = [
    ROOT / "docs/referencias/paseo.md",
    ROOT / "docs/explicacoes/por-que-paseo.md",
    ROOT / "docs/guias/acesso-remoto.md",
    ROOT / "docs/guias/voz-com-openai.md",
    ROOT / "docs/tutoriais/acesso-pelo-celular.md",
]


def test_cinco_docs_declaram_paseo_080_em_2026_09_13():
    for path in DOCS:
        texto = path.read_text(encoding="utf-8")
        corpo = texto.split("# ", 1)[-1]
        antes = corpo.split("\n## ", 1)[0]
        assert "0.8.0" in antes, f"{path.name}: 0.8.0 não está antes do primeiro H2"
        assert "2026-09-13" in antes, f"{path.name}: 2026-09-13 não está antes do primeiro H2"


def test_referencia_diz_que_a_skill_chama():
    texto = (ROOT / "docs/referencias/paseo.md").read_text(encoding="utf-8")
    assert "chama" in texto.lower()
    assert "paseo-configurar" in texto
