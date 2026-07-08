from koine import schema


def test_escopo_from_fm():
    e = schema.Escopo.from_fm({"nome": "fixture", "pasta-referencias": "home:refs"})
    assert e.nome == "fixture"
    assert e.pasta_referencias == "home:refs"


def test_dominio_sinopse():
    d = schema.Dominio.from_fm({"title": "Tecnologia", "sinopse": "Conhecimento técnico."})
    assert d.sinopse == "Conhecimento técnico."
