from koine import adapters, shell


def test_todo_adapter_declara_os_degraus_que_aceita():
    # Tabela paralela envelhece sozinha: adapter novo entra no REGISTRY e a
    # decisão de pré-requisitos passaria a mentir sobre ele em silêncio.
    for nome, mod in adapters.REGISTRY.items():
        assert hasattr(mod, "ACEITA_SHELL"), f"{nome} não declara ACEITA_SHELL"
        assert all(d in shell.ESCADA for d in mod.ACEITA_SHELL), nome


def test_o_cmd_so_serve_ao_opencode():
    # Medido em 28/08: o claude aceita bash/zsh apenas, e copilot, codex e agy
    # só PowerShell. Nenhum dos quatro tem o cmd como opção.
    for nome, mod in adapters.REGISTRY.items():
        if nome == "opencode":
            assert shell.CMD in mod.ACEITA_SHELL
        else:
            assert shell.CMD not in mod.ACEITA_SHELL, nome


def test_claude_aceita_bash_e_os_tres_do_powershell_nao():
    assert shell.BASH in adapters.REGISTRY["claude"].ACEITA_SHELL
    for nome in ("copilot", "codex", "agy"):
        assert shell.BASH not in adapters.REGISTRY[nome].ACEITA_SHELL, nome
