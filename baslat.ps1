# Claude Code'u bulur (yoksa kurar), PATH'i duzeltir ve bu klasorde acar.
# 2-KANAL-YONETICISI.bat ve 3-YENI-VIDEO.bat bunu calistirir. kurulum.ps1 de -SadeceKur ile cagirir.
param([string]$Komut = "", [switch]$SadeceKur)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
Set-Location -Path $PSScriptRoot
$Log = Join-Path $PSScriptRoot "_teshis.txt"
function Yaz($m, $renk = "Gray") { Write-Host $m -ForegroundColor $renk; Add-Content -Path $Log -Value $m -Encoding UTF8 }
Set-Content -Path $Log -Value ("baslat.ps1 " + (Get-Date -Format s)) -Encoding UTF8

# 1) Ajan/skill paketi yerinde mi?
# paket guncellendiyse (imzasi degistiyse) yeniden ac
if (Test-Path "ayar-paketi.zip") {
    $imza = (Get-FileHash "ayar-paketi.zip" -Algorithm SHA256).Hash
    $imzaDosya = ".claude\paket-imza.txt"
    $eski = if (Test-Path $imzaDosya) { (Get-Content $imzaDosya -Raw).Trim() } else { "" }
    if (-not (Test-Path ".claude\skills") -or $eski -ne $imza) {
        Expand-Archive -Path "ayar-paketi.zip" -DestinationPath . -Force
        Set-Content -Path $imzaDosya -Value $imza -Encoding ASCII
        Yaz "Ajan ve skill dosyalari guncellendi."
    }
}

# 2) Claude Code nerede?
function ClaudeBul {
    $k = Get-Command claude -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($k) { return $k.Source }
    $adaylar = @(
        (Join-Path $env:USERPROFILE ".local\bin\claude.exe"),
        (Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Links\claude.exe"),
        (Join-Path $env:APPDATA "npm\claude.cmd")
    )
    foreach ($a in $adaylar) { if (Test-Path -LiteralPath $a) { return $a } }
    return $null
}

function PathaEkle($klasor) {
    $kalici = [Environment]::GetEnvironmentVariable("Path", "User")
    if (-not $kalici) { $kalici = "" }
    if (($kalici -split ";") -notcontains $klasor) {
        [Environment]::SetEnvironmentVariable("Path", ($kalici.TrimEnd(";") + ";" + $klasor).TrimStart(";"), "User")
        Yaz "PATH'e eklendi: $klasor"
    }
    if (($env:Path -split ";") -notcontains $klasor) { $env:Path = "$env:Path;$klasor" }
}

$claude = ClaudeBul
if (-not $claude) {
    Yaz "Claude Code bulunamadi, simdi kuruluyor (1-3 dk, ekranda ilerleme gorunmeyebilir)..." "Yellow"
    # ayri bir PowerShell icinde: kurulum betigi "exit" derse bu pencere kapanmasin
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://claude.ai/install.ps1 | iex"
    $claude = ClaudeBul
    if (-not $claude -and (Get-Command winget -ErrorAction SilentlyContinue)) {
        Yaz "Ikinci yol deneniyor: winget ile kurulum..." "Yellow"
        winget install -e --id Anthropic.ClaudeCode --accept-source-agreements --accept-package-agreements
        $claude = ClaudeBul
    }
}

if (-not $claude) {
    Yaz "`nClaude Code kurulamadi." "Red"
    Yaz "Bu pencerenin ekran goruntusunu Claude'a gonder; _teshis.txt dosyasi da bu klasorde." "Red"
    exit 9
}

PathaEkle (Split-Path -Parent $claude)
$surum = & $claude --version 2>&1
Yaz "Claude Code: $surum ($claude)" "Green"

if ($SadeceKur) { exit 0 }

# 3) Ac
Yaz "`nClaude aciliyor. Ilk seferde tarayicida Claude hesabinla giris yapman istenir." "Cyan"
Yaz "Cikmak icin /exit yaz veya pencereyi kapat.`n" "Cyan"
if ($Komut) { & $claude $Komut } else { & $claude }
exit 0
