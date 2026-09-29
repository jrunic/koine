import os

from koine import dircopy


def test_arvore_devolve_conteudo_por_caminho_relativo(tmp_path):
    base = tmp_path / "base"
    (base / "sub").mkdir(parents=True)
    (base / "a.txt").write_text("A")
    (base / "sub" / "b.txt").write_text("B")

    resultado = dircopy.arvore(str(base))

    assert resultado == {"a.txt": b"A", os.path.join("sub", "b.txt"): b"B"}


def test_arvore_identica_para_duas_copias_iguais(tmp_path):
    origem = tmp_path / "origem"
    origem.mkdir()
    (origem / "x.txt").write_text("conteudo")
    destino = tmp_path / "destino"
    destino.mkdir()
    (destino / "x.txt").write_text("conteudo")

    assert dircopy.arvore(str(origem)) == dircopy.arvore(str(destino))


def test_trocar_dir_substitui_conteudo_do_destino(tmp_path):
    origem = tmp_path / "origem"
    origem.mkdir()
    (origem / "novo.txt").write_text("v2")
    destino = tmp_path / "destino"
    destino.mkdir()
    (destino / "velho.txt").write_text("v1")

    dircopy.trocar_dir(str(origem), str(destino))

    assert os.listdir(destino) == ["novo.txt"]
    assert (destino / "novo.txt").read_text() == "v2"


def test_trocar_dir_nao_deixa_temporario_orfao(tmp_path):
    origem = tmp_path / "origem"
    origem.mkdir()
    (origem / "a.txt").write_text("a")
    destino = tmp_path / "destino"
    destino.mkdir()

    dircopy.trocar_dir(str(origem), str(destino))

    restantes = sorted(os.listdir(tmp_path))
    assert restantes == ["destino", "origem"]
