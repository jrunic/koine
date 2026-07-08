@echo off
REM install.bat — wrapper para install.ps1, contorna ExecutionPolicy restrito.
REM Uso em cmd quando PowerShell scripts são bloqueados por default.
REM Instala o Koine (aplicação Python) — requer Python >= 3.12 no PATH.
REM Limitação declarada: baixa o install.ps1 de releases/latest/download —
REM enquanto "latest" for a v0.3.2, serve o ps1 velho (Go); o fluxo .bat só é
REM íntegro depois que a v0.4.0 virar latest (validar no smoke pós-publicação).
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "iwr -useb https://github.com/jrunic/koine/releases/latest/download/install.ps1 | iex"
