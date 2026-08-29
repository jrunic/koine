from koine import mensagens
from koine import prerequisitos as pre


def test_o_relatorio_diz_que_o_git_bash_nao_salva_os_tres():
    # Sem esta frase o usuário instala o Git Bash e continua quebrado.
    txt = mensagens.relatorio_prerequisitos([pre.Achado("copilot", pre.SEM_SHELL)])
    assert "Git Bash" in txt
    assert "copilot" in txt


def test_a_orientacao_do_git_bash_traz_link_e_arquivo_por_arquitetura():
    amd = mensagens.relatorio_prerequisitos(
        [pre.Achado("claude", pre.CLAUDE_SEM_BASH)], arquitetura="AMD64")
    assert "https://git-scm.com/download/win" in amd
    assert "64-bit Git for Windows Setup" in amd
    assert "administrador" in amd          # não precisa de admin
    assert "local padrão" in amd           # o claude sonda a instalação, não o PATH

    arm = mensagens.relatorio_prerequisitos(
        [pre.Achado("claude", pre.CLAUDE_SEM_BASH)], arquitetura="ARM64")
    assert "ARM64 Git for Windows Setup" in arm


def test_relatorio_sem_achado_nao_alarma():
    txt = mensagens.relatorio_prerequisitos([])
    assert "Git Bash" not in txt
    assert txt.strip() != ""   # diz que está tudo certo, em vez de sumir


def test_o_aviso_do_launch_e_uma_linha_e_diz_que_a_sessao_sobe():
    linha = mensagens.aviso_launch_sem_shell("copilot")
    assert linha.count("\n") <= 1
    assert "copilot" in linha
    assert "abre" in linha


def test_o_aviso_do_claude_aponta_o_remedio():
    linha = mensagens.aviso_launch_sem_shell("claude", pre.CLAUDE_SEM_BASH)
    assert "Git Bash" in linha
    assert "git-scm.com" in linha
