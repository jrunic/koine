import io
import os
import stat

import pytest

from koine import pasta


def test_resolver_vazio_e_pwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert pasta.resolver("") == os.getcwd()


def test_resolver_path_direto(tmp_path):
    d = tmp_path / "sub"; d.mkdir()
    assert pasta.resolver(str(d)) == os.path.abspath(str(d))


def test_resolver_alias(tmp_path, monkeypatch):
    home = str(tmp_path); monkeypatch.setenv("HOME", home)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    from koine import aliases
    os.makedirs(os.path.join(home, "koine"))
    aliases.adicionar("koine", "koine", "home")     # ~/koine
    assert pasta.resolver("koine") == os.path.join(home, "koine")


def _home_com_pastas(tmp_path, monkeypatch, rels):
    home = tmp_path / "home"
    for r in rels:
        os.makedirs(home / r, exist_ok=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    return str(home)


def test_listar_candidatos_pula_dotdirs_e_ignoradas(tmp_path, monkeypatch):
    home = _home_com_pastas(tmp_path, monkeypatch,
                            ["projetos/koine", ".config/koine", "app/node_modules/x", "app"])
    cands = pasta.listar_candidatos()
    assert os.path.join(home, "projetos", "koine") in cands
    assert os.path.join(home, "app") in cands
    assert not any(".config" in c or "node_modules" in c for c in cands)


def test_listar_candidatos_limita_profundidade(tmp_path, monkeypatch):
    # fronteira EXATA (advisor finding 4): n6 tem prof 7 (incluído), n7 tem prof 8 (excluído)
    fundo = "/".join(f"n{i}" for i in range(8))  # n0..n7
    home = _home_com_pastas(tmp_path, monkeypatch, [fundo])
    cands = pasta.listar_candidatos()
    assert any(c.endswith("n6") for c in cands)      # prof 7 — dentro do limite
    assert not any(c.endswith("n7") for c in cands)  # prof 8 — podado


def test_listar_candidatos_ordem_lexical(tmp_path, monkeypatch):
    # WalkDir do Go é lexical; os.walk é arbitrário → sorted obrigatório (finding 3)
    home = _home_com_pastas(tmp_path, monkeypatch, ["zeta", "alfa", "media"])
    cands = pasta.listar_candidatos()
    assert cands == sorted(cands)


def test_fuzzy_filter_match_por_palavra_exata():
    cands = ["/h/criar-koine", "/h/koine", "/h/koinezada", "/h/outra"]
    assert pasta.fuzzy_filter("koine", cands) == ["/h/criar-koine", "/h/koine"]
    assert pasta.fuzzy_filter("criar-koine", cands) == ["/h/criar-koine", "/h/koine"]


def test_escolher_menu_zero_e_um():
    with pytest.raises(pasta.ResolucaoErro):
        pasta.escolher_menu([])
    assert pasta.escolher_menu(["/h/unica"]) == "/h/unica"


def test_escolher_menu_numerado(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("PATH", "/usr/bin:/bin")  # sem fzf
    monkeypatch.setattr("sys.stdin", io.StringIO("2\n"))
    assert pasta.escolher_menu(["/h/a", "/h/b"]) == "/h/b"
    out = capsys.readouterr().out
    assert "  1) /h/a" in out and "  2) /h/b" in out and "Número: " in out


def test_escolher_menu_numerado_invalido(monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin:/bin")
    monkeypatch.setattr("sys.stdin", io.StringIO("x\n"))
    with pytest.raises(pasta.ResolucaoErro):
        pasta.escolher_menu(["/h/a", "/h/b"])


def test_escolher_menu_fzf(tmp_path, monkeypatch):
    fzf = tmp_path / "bin" / "fzf"
    os.makedirs(fzf.parent)
    fzf.write_text("#!/bin/sh\nhead -1\n")  # devolve o 1º candidato
    fzf.chmod(fzf.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{fzf.parent}:/usr/bin:/bin")
    assert pasta.escolher_menu(["/h/a", "/h/b"]) == "/h/a"


def test_oferecer_salvar_alias_default_sim(tmp_path, monkeypatch, capsys):
    home = _home_com_pastas(tmp_path, monkeypatch, ["proj"])
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    monkeypatch.setattr("sys.stdin", io.StringIO("\n"))
    pasta.oferecer_salvar_alias("proj", os.path.join(home, "proj"))
    from koine import aliases
    a = aliases.carregar()
    assert a["pastas"]["proj"] == {"path": "proj", "from": "home"}
    assert "Alias 'proj' salvo." in capsys.readouterr().out


def test_oferecer_salvar_alias_recusa(tmp_path, monkeypatch):
    home = _home_com_pastas(tmp_path, monkeypatch, ["proj"])
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    monkeypatch.setattr("sys.stdin", io.StringIO("n\n"))
    pasta.oferecer_salvar_alias("proj", os.path.join(home, "proj"))
    from koine import aliases
    assert "proj" not in aliases.carregar()["pastas"]


def test_resolver_fuzzy_fim_a_fim(tmp_path, monkeypatch):
    home = _home_com_pastas(tmp_path, monkeypatch, ["projetos/criar-koine"])
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    monkeypatch.setattr("sys.stdin", io.StringIO("\n"))   # aceita salvar alias
    monkeypatch.chdir(home)
    assert pasta.resolver("koine") == os.path.join(home, "projetos", "criar-koine")


def test_resolver_sem_match_erro(tmp_path, monkeypatch):
    _home_com_pastas(tmp_path, monkeypatch, ["outra"])
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    with pytest.raises(pasta.ResolucaoErro, match="não resolveu para nenhuma pasta"):
        pasta.resolver("zzz-inexistente")
