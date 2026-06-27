@echo off
REM install.bat — wrapper para install.ps1, contorna ExecutionPolicy restrito.
REM Uso em cmd quando PowerShell scripts são bloqueados por default.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "iwr -useb https://github.com/jrunic/koine/releases/latest/download/install.ps1 | iex"
