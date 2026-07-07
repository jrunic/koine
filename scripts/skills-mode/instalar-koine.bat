@echo off
setlocal
echo === Instalador Koine (modo skills) ===

set "SRC=%~dp0.koine-bootstrap"
set "DATA=%USERPROFILE%\.local\share\koine"
set "CONF=%USERPROFILE%\.config\koine"
set "SKILLS=%USERPROFILE%\.claude\skills"

if not exist "%SRC%" (
  echo ERRO: pasta .koine-bootstrap nao encontrada ao lado deste .bat.
  echo Descompacte o zip em %%USERPROFILE%%\koine e rode novamente.
  exit /b 1
)

echo Criando diretorios...
if not exist "%DATA%\agentes"    mkdir "%DATA%\agentes"
if not exist "%DATA%\conceitos"  mkdir "%DATA%\conceitos"
if not exist "%CONF%\dominios"   mkdir "%CONF%\dominios"
if not exist "%CONF%\escopos"    mkdir "%CONF%\escopos"
if not exist "%CONF%\agentes"    mkdir "%CONF%\agentes"
if not exist "%SKILLS%"          mkdir "%SKILLS%"

echo Copiando conteudo do vault...
copy /Y "%SRC%\KOINE.md" "%DATA%\KOINE.md" >nul
xcopy /E /I /Y "%SRC%\agentes"   "%DATA%\agentes"   >nul
xcopy /E /I /Y "%SRC%\conceitos" "%DATA%\conceitos" >nul
xcopy /E /I /Y "%SRC%\dominios"  "%CONF%\dominios"  >nul

echo Instalando skills kn-*...
xcopy /E /I /Y "%SRC%\habilidades\kn-*" "%SKILLS%" >nul

echo.
echo Verificacao:
if exist "%DATA%\KOINE.md"                echo   [ok] KOINE.md
if exist "%DATA%\agentes\hermes.md"       echo   [ok] hermes.md
if exist "%DATA%\conceitos\escopos.md"    echo   [ok] conceitos
if exist "%CONF%\dominios\universal.md"   echo   [ok] dominios
if exist "%SKILLS%\kn-01-recebe-usuario"  echo   [ok] skills

echo.
echo Instalacao concluida. Abra o Claude Code nesta pasta:
echo   cd %%USERPROFILE%%\koine ^&^& claude
echo Hermes iniciara o onboarding automaticamente.
endlocal
