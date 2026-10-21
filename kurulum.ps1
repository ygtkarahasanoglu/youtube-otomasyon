# YouTube otomasyon - Windows kurulumu (1-KURULUM.bat bunu calistirir)
# Python, Git, ffmpeg, Python paketleri ve Claude Code'u kurar; sonra kontrol yapar.

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
Set-Location -Path $PSScriptRoot

# Claude ayarlari, ajanlar ve skill'ler (.claude, .vscode, .env.ornek) bu paketin icinde
if (Test-Path "ayar-paketi.zip") { Expand-Archive -Path "ayar-paketi.zip" -DestinationPath . -Force; Write-Host "Ajan ve skill dosyalari yerlestirildi." }

function Adim($m) { Write-Host "`n==> $m" -ForegroundColor Cyan }
function Var($k) { [bool](Get-Command $k -ErrorAction SilentlyContinue) }

function PythonBul {
    foreach ($aday in @("python", "py")) {
        if (Var $aday) {
            $s = & $aday --version 2>&1
            if ($LASTEXITCODE -eq 0 -and "$s" -match "Python 3\.(\d+)" -and [int]$Matches[1] -ge 10) { return $aday }
        }
    }
    return $null
}

if (-not (Var winget)) {
    Write-Host "winget bulunamadi. Microsoft Store'dan 'Uygulama Yukleyicisi' (App Installer) uygulamasini guncelle, sonra tekrar calistir." -ForegroundColor Yellow
    exit 1
}

Adim "Python"
$PY = PythonBul
if (-not $PY) {
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements --override "/passive PrependPath=1 Include_launcher=1"
    Write-Host "`nPython kuruldu. Bu pencereyi KAPAT ve 1-KURULUM.bat dosyasini TEKRAR calistir." -ForegroundColor Yellow
    exit 0
}
& $PY --version

Adim "Git (Claude Code icin)"
if (-not (Var git)) { winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements } else { git --version }

Adim "ffmpeg (video birlestirme)"
if (-not (Var ffmpeg)) { winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements } else { Write-Host "ffmpeg kurulu" }

Adim "Python paketleri"
& $PY -m pip install --upgrade pip --quiet
& $PY -m pip install -U -r requirements.txt

Adim "Turkce karakter ayari"
setx PYTHONUTF8 1 | Out-Null
Write-Host "PYTHONUTF8=1"

Adim "Claude Code"
& (Join-Path $PSScriptRoot "baslat.ps1") -SadeceKur

Adim "Kontrol"
& $PY -m hat kontrol

Write-Host "`nKurulum bitti." -ForegroundColor Green
Write-Host "Sonra 2-KANAL-YONETICISI.bat dosyasina cift tikla ve /kurulum yaz." -ForegroundColor Green
