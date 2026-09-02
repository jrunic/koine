import os
from koine import paths


def test_vault_dir_respeita_xdg(monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", "/x/data")
    assert paths.vault_dir() == os.path.join("/x/data", "koine")


def test_vault_dir_fallback_home(monkeypatch):
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setenv("HOME", "/h")
    assert paths.vault_dir() == os.path.join("/h", ".local", "share", "koine")


def test_config_dir_fallback_home(monkeypatch):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setenv("HOME", "/h")
    assert paths.config_dir() == os.path.join("/h", ".config", "koine")


def test_tagged_home(monkeypatch):
    monkeypatch.setenv("HOME", "/h")
    assert paths.resolver_tagged("home:refs") == os.path.join("/h", "refs")


def test_tagged_sem_prefixo_e_erro():
    import pytest
    with pytest.raises(ValueError):
        paths.resolver_tagged("refs")


def test_ambiente_de_teste_sem_xdg():
    # Guarda de recorrência: runners CI (GitHub Actions ubuntu) exportam XDG_*.
    # paths.py honra XDG_* ANTES de HOME, então qualquer XDG_* visível em
    # os.environ vaza para subprocessos ({**os.environ, "HOME": ...}) e
    # quebra o isolamento por HOME dos fixtures. conftest._isola_xdg limpa.
    assert not [k for k in os.environ if k.startswith("XDG_")]


# --- known folder do Windows na resolução do tagged (jd-task #762) ----------

def _sem_kfm(_segmento, **kw):
    return None


def _com_kfm(segmento, **kw):
    return "C:\\u\\OneDrive - ACME\\Documents" if segmento.lower() == "documents" else None


def test_sem_redirecionamento_o_caminho_e_o_de_sempre(monkeypatch, tmp_path):
    """Critério 1 da spec: no-op onde funciona. É o teste que dá poder ao par —
    sem ele, uma implementação que resolvesse SEMPRE passaria."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    r = paths.resolver_tagged_detalhado("home:Documents/CURSO IA",
                                        resolver_known=_sem_kfm)
    assert r.caminho == os.path.join(str(tmp_path), "Documents/CURSO IA")
    assert not r.divergiu


def test_com_redirecionamento_o_caminho_vai_para_a_known_folder(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    r = paths.resolver_tagged_detalhado("home:Documents/CURSO IA",
                                        resolver_known=_com_kfm)
    assert r.caminho == os.path.join("C:\\u\\OneDrive - ACME\\Documents", "CURSO IA")
    assert r.divergiu
    assert r.concatenado == os.path.join(str(tmp_path), "Documents/CURSO IA")


def test_primeiro_segmento_que_nao_casa_fica_intocado(monkeypatch, tmp_path):
    """Critério 7: é o estado da máquina de produção DEPOIS do conserto manual —
    o escopo aponta para dentro do OneDrive por caminho literal. Não pode mudar."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    r = paths.resolver_tagged_detalhado("home:OneDrive - ACME/Documents/CURSO IA",
                                        resolver_known=_com_kfm)
    assert r.caminho == os.path.join(str(tmp_path), "OneDrive - ACME/Documents/CURSO IA")
    assert not r.divergiu


def test_resolver_tagged_continua_devolvendo_string(monkeypatch, tmp_path):
    """A assinatura antiga não muda: três chamadores dependem dela."""
    monkeypatch.setenv("HOME", str(tmp_path))
    assert isinstance(paths.resolver_tagged("abs:/x/y"), str)


def test_mesmo_caminho_com_separadores_diferentes_nao_e_divergencia():
    """Defeito achado pelo gate de bancada em 02/09/2026, e invisível no macOS.

    No Windows a concatenação preservava a `/` que o usuário escreveu no tagged
    path (`Documents/CURSO IA`) enquanto o caminho resolvido saía com `\\` — as
    duas strings diferentes apontando para a MESMA pasta. O aviso de
    redirecionamento disparava numa máquina sem redirecionamento nenhum.

    Em POSIX isso não reproduz: `os.path.join` usa `/` nos dois lados. Por isso a
    comparação é sobre separador unificado, e não sobre a string crua.
    """
    r = paths.Resolucao(caminho="C:\\u\\Documents\\CURSO IA",
                        concatenado="C:\\u\\Documents/CURSO IA")
    assert not r.divergiu


def test_caminho_realmente_diferente_continua_divergindo():
    """Metade de poder: sem ela, um `divergiu` que devolvesse sempre False passaria."""
    r = paths.Resolucao(caminho="C:\\u\\OneDrive\\Documents",
                        concatenado="C:\\u\\Documents")
    assert r.divergiu
