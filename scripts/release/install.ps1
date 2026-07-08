# install.ps1 — instala o Koine (aplicação Python) a partir do GitHub Release.
# Baixa koine-<versao>.zip (koine.pyz + vault/), extrai para o diretório de
# dados do Koine e delega ao `koine instalar`.
# Overrides: $env:KOINE_VERSAO = "v0.4.0" (pina a tag); $env:KOINE_BASE_URL (espelho)
# Documentação: https://github.com/jrunic/koine

$ErrorActionPreference = "Stop"

$repo = "jrunic/koine"
$dataDir = Join-Path $env:USERPROFILE ".local\share\koine"
$dest = Join-Path $dataDir "dist"
$binDir = Join-Path $env:USERPROFILE ".local\bin"

# 1. Localiza um Python >= 3.12
function Test-Python312 {
    param([string]$Exe, [string[]]$Extra)
    try {
        & $Exe @Extra "-c" "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)" 2>$null | Out-Null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

$py = $null
$pyArgs = @()
if ((Get-Command py -ErrorAction SilentlyContinue) -and (Test-Python312 "py" @("-3"))) {
    $py = "py"; $pyArgs = @("-3")
}
if (-not $py) {
    foreach ($cand in @("python", "python3")) {
        if ((Get-Command $cand -ErrorAction SilentlyContinue) -and (Test-Python312 $cand @())) {
            $py = $cand
            break
        }
    }
}
if (-not $py) {
    Write-Host "Erro: nenhum Python >= 3.12 encontrado no PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "O Koine é uma aplicação Python. Como instalar:"
    Write-Host "  - Baixe de https://www.python.org/downloads/ e marque 'Add python.exe to PATH'"
    Write-Host "  - Em estação corporativa: peça o Python >= 3.12 à sua TI"
    Write-Host ""
    Write-Host "Depois rode este script novamente. Nada foi instalado."
    exit 1
}

# 2. Resolve a tag a instalar (default: última release)
$tag = $env:KOINE_VERSAO
if (-not $tag) {
    $rel = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/releases/latest" -UseBasicParsing
    $tag = $rel.tag_name
}
$versao = $tag.TrimStart("v")
$asset = "koine-$versao.zip"
$baseUrl = if ($env:KOINE_BASE_URL) { $env:KOINE_BASE_URL } else { "https://github.com/$repo/releases/download" }
$url = "$baseUrl/$tag/$asset"

# 3. Baixa para tmp — nada é tocado se o download falhar
$tmpZip = Join-Path ([System.IO.Path]::GetTempPath()) $asset
Write-Host "Baixando $asset..."
try {
    Invoke-WebRequest -Uri $url -OutFile $tmpZip -UseBasicParsing
} catch {
    Write-Error "Falha ao baixar $url`: $_"
    Write-Host "Verifique sua conexão ou tente novamente. Nada foi instalado." -ForegroundColor Red
    exit 1
}

# 4. Extrai para o local canônico do pacote
if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Expand-Archive -Path $tmpZip -DestinationPath $dest -Force
Remove-Item $tmpZip

$pyz = Join-Path $dest "koine.pyz"
$versionOutput = & $py @pyArgs $pyz versao
Write-Host "✓ Pacote extraído em $dest"
Write-Host "  $versionOutput"
Write-Host ""

# 5. Delegar ao instalador do produto
& $py @pyArgs $pyz instalar
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# 6. PATH (user env, persistente)
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if (($userPath -split ";") -notcontains $binDir) {
    Write-Host ""
    Write-Host "⚠️  $binDir não está no seu PATH." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Rode este comando uma vez (sem admin, persiste para o usuário):"
    Write-Host ""
    Write-Host '    [Environment]::SetEnvironmentVariable("PATH", "$env:USERPROFILE\.local\bin;" + [Environment]::GetEnvironmentVariable("PATH", "User"), "User")'
    Write-Host ""
    Write-Host "  Depois reabra o terminal."
}
