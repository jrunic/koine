# install.ps1 — instala kn-agente em %USERPROFILE%\.local\bin\ a partir do GitHub Release.
# Documentação: https://github.com/jrunic/koine

$ErrorActionPreference = "Stop"

$repo = "jrunic/koine"
$destDir = Join-Path $env:USERPROFILE ".local\bin"
$dest = Join-Path $destDir "kn-agente.exe"
$asset = "kn-agente-windows-amd64.exe"
$url = "https://github.com/$repo/releases/latest/download/$asset"

Write-Host "Baixando $asset..."

# Cria diretório destino
New-Item -ItemType Directory -Force -Path $destDir | Out-Null

# Download
try {
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
}
catch {
    Write-Error "Falha ao baixar $url`: $_"
    Write-Host "Verifique sua conexão ou tente novamente." -ForegroundColor Red
    exit 1
}

# Valida
$versionOutput = & $dest --versao 2>&1
Write-Host "✓ Instalado em $dest"
Write-Host "  $versionOutput"
Write-Host ""

# Verifica PATH (user env, persistente)
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$pathParts = $userPath -split ";"
$pathOK = $pathParts -contains $destDir

if ($pathOK) {
    Write-Host "Próximo passo: rode 'kn-agente instalar'"
}
else {
    Write-Host "⚠️  $destDir não está no seu PATH." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Rode este comando uma vez (sem admin, persiste para o usuário):"
    Write-Host ""
    Write-Host '    [Environment]::SetEnvironmentVariable("PATH", "$env:USERPROFILE\.local\bin;" + [Environment]::GetEnvironmentVariable("PATH", "User"), "User")'
    Write-Host ""
    Write-Host "  Depois reabra o terminal e rode: kn-agente instalar"
}
