@echo off
setlocal EnableExtensions
REM install.bat - instala o Koine (aplicacao Python) a partir do GitHub Release.
REM
REM Totalmente cmd.exe: NAO usa PowerShell. Estacao corporativa que bloqueia o
REM powershell.exe por politica roda este script sem admin.
REM
REM Requisitos: Python >= 3.12 no PATH e curl.exe (Windows 10 1803+).
REM Overrides:  set KOINE_VERSAO=v0.6.1   (pina a tag)
REM             set KOINE_INSTALAR_ARGS=--nao-interativo
REM                 (repassado ao "koine instalar"; use para instalar
REM                  sem nenhuma pergunta, em automacao)
REM             set KOINE_BASE_URL=<url>  (espelho interno)
REM Documentacao: https://github.com/jrunic/koine
REM
REM Este arquivo e ASCII puro de proposito: o cmd.exe le .bat na codepage OEM
REM (850/437), e acento ou travessao em UTF-8 sai como lixo na tela.

set "REPO=jrunic/koine"
set "DEST=%USERPROFILE%\.local\share\koine\dist"
set "BINDIR=%USERPROFILE%\.local\bin"
set "TMPZIP="

REM ---------------------------------------------------------------- 1. curl
where curl.exe >nul 2>nul
if errorlevel 1 goto sem_curl

REM ------------------------------------------------- 2. Python >= 3.12 no PATH
set "PY="
set "PYARG="
call :testa_python py -3
call :testa_python python
call :testa_python python3
if not defined PY goto sem_python

REM ------------------------------------------------------ 3. Resolve a versao
set "TAG=%KOINE_VERSAO%"
if not defined TAG goto resolve_tag
REM Aceita KOINE_VERSAO com ou sem o "v" (v0.6.2 e 0.6.2 valem). Esta
REM linha fica fora do "if defined" de proposito: o cmd expande a linha
REM INTEIRA antes de avaliar a condicao, e "%TAG:~0,1%" com TAG vazia e
REM erro de sintaxe fatal - medido na bancada Windows em 26/08/2026.
if /i not "%TAG:~0,1%"=="v" set "TAG=v%TAG%"
goto tem_tag

:resolve_tag
set "URLFINAL="
for /f "usebackq delims=" %%i in (`curl -fsSLSI -o NUL -w "%%{url_effective}" "https://github.com/%REPO%/releases/latest"`) do set "URLFINAL=%%i"
if not defined URLFINAL goto sem_versao
set "TAG=%URLFINAL:*/tag/=%"

:tem_tag
echo %TAG%| findstr /r /c:"^v[0-9]" >nul
if errorlevel 1 goto sem_versao

set "VERSAO=%TAG:~1%"
set "ASSET=koine-%VERSAO%.zip"
if not defined KOINE_BASE_URL set "KOINE_BASE_URL=https://github.com/%REPO%/releases/download"
set "URL=%KOINE_BASE_URL%/%TAG%/%ASSET%"

REM ------------------- 4. Baixa para o TEMP - nada e tocado se o download falha
set "TMPZIP=%TEMP%\%ASSET%"
echo Baixando %ASSET% ...
curl -fLSs --retry 3 -o "%TMPZIP%" "%URL%"
if errorlevel 1 goto falha_download

REM ------------------------------------------ 5. Extrai para o local canonico
if exist "%DEST%" rmdir /s /q "%DEST%"
mkdir "%DEST%" 2>nul
if not exist "%DEST%" goto falha_pasta
"%PY%" %PYARG% -m zipfile -e "%TMPZIP%" "%DEST%"
if errorlevel 1 goto falha_extracao
del /q "%TMPZIP%" 2>nul
set "TMPZIP="

if not exist "%DEST%\koine.pyz" goto falha_pacote
echo Pacote extraido em %DEST%
"%PY%" %PYARG% "%DEST%\koine.pyz" versao
echo.

REM --------------------------------------- 6. Delega ao instalador do produto
"%PY%" %PYARG% "%DEST%\koine.pyz" instalar %KOINE_INSTALAR_ARGS%
if errorlevel 1 goto falha_instalar

REM ------------------------------------------------------------- 7. PATH
REM Quem decide sobre o PATH do usuario e o `koine instalar` (secao 6): ele
REM compara contra o REGISTRO, que e a verdade duravel, e escreve se faltar.
REM O .bat nao repete esse aviso porque so enxerga a sessao - e foi assim que
REM ele passou a dizer que a pasta faltava com ela ja no registro.
REM
REM O que so o .bat pode fazer: consertar a PROPRIA sessao. Processo filho nao
REM altera o ambiente do pai, entao o python que rodou o instalar nao tem como
REM mexer no %PATH% daqui.
set "PATH=%BINDIR%;%PATH%"
goto fim

REM ====================================================== rotinas e mensagens

:testa_python
REM Marca em PY/PYARG o primeiro interpretador >= 3.12 achado. Nao sobrescreve.
if defined PY goto :eof
where %1 >nul 2>nul
if errorlevel 1 goto :eof
%1 %2 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>nul
if errorlevel 1 goto :eof
for /f "usebackq delims=" %%p in (`%1 %2 -c "import sys; print(sys.executable)"`) do set "PY=%%p"
set "PYARG="
goto :eof

:sem_curl
echo Erro: curl.exe nao foi encontrado neste sistema.
echo.
echo O curl.exe acompanha o Windows 10 versao 1803 e posteriores. Se este
echo Windows e mais antigo, ou se o curl foi removido:
echo   - atualize o Windows, ou
echo   - baixe o pacote a mao seguindo o passo a passo em
echo     https://github.com/jrunic/koine/blob/main/docs/guias/instalacao.md
echo.
echo Nada foi instalado.
exit /b 1

:sem_python
echo Erro: nenhum Python ^>= 3.12 encontrado no PATH.
echo.
echo O Koine e uma aplicacao Python. Como instalar:
echo   - baixe de https://www.python.org/downloads/ e marque
echo     "Add python.exe to PATH" durante a instalacao
echo   - em estacao corporativa: peca o Python 3.12 ou superior a sua TI
echo.
echo Confira depois com:  python --version
echo Rode este script novamente. Nada foi instalado.
exit /b 1

:sem_versao
echo Erro: nao foi possivel descobrir a ultima versao do Koine.
echo.
echo Em geral e falta de rede, DNS ou proxy corporativo bloqueando o github.com.
echo   - teste:  curl -I https://github.com/%REPO%/releases/latest
echo   - se sua rede exige proxy, defina antes:  set HTTPS_PROXY=http://host:porta
echo   - ou informe a versao a mao:  set KOINE_VERSAO=v0.6.1 ^&^& install.bat
echo.
echo Nada foi instalado.
exit /b 1

:falha_download
echo Erro: falha ao baixar %URL%
echo.
echo   - confira a conexao e tente de novo
echo   - se a versao foi fixada em KOINE_VERSAO, confira se a tag existe em
echo     https://github.com/%REPO%/releases
echo   - atras de proxy corporativo, defina:  set HTTPS_PROXY=http://host:porta
echo.
echo Nada foi instalado.
if defined TMPZIP del /q "%TMPZIP%" 2>nul
exit /b 1

:falha_pasta
echo Erro: nao foi possivel criar a pasta %DEST%
echo.
echo   - confira se voce tem permissao de escrita em %USERPROFILE%
echo   - feche programas que possam estar usando essa pasta e tente de novo
echo.
echo Nada foi instalado.
if defined TMPZIP del /q "%TMPZIP%" 2>nul
exit /b 1

:falha_extracao
echo Erro: falha ao extrair %ASSET% em %DEST%
echo.
echo O download pode ter vindo corrompido, ou um antivirus bloqueou a escrita.
echo Rode o script novamente; se repetir, mande a mensagem acima junto.
echo.
echo Instalacao incompleta - o Koine anterior, se existia, foi removido.
if defined TMPZIP del /q "%TMPZIP%" 2>nul
exit /b 1

:falha_pacote
echo Erro: o pacote baixado nao contem koine.pyz.
echo.
echo Isso indica asset errado ou download truncado. Tente de novo; se repetir,
echo fixe uma versao conhecida:  set KOINE_VERSAO=v0.6.1 ^&^& install.bat
echo.
echo Instalacao incompleta.
exit /b 1

:falha_instalar
echo.
echo Erro: o pacote foi extraido em %DEST%, mas "koine instalar" falhou.
echo.
echo A mensagem do proprio Koine esta logo acima - ela diz o que faltou.
echo Depois de resolver, voce pode repetir so a ultima etapa:
echo     "%PY%" "%DEST%\koine.pyz" instalar
echo.
exit /b 1

:fim
endlocal
exit /b 0
