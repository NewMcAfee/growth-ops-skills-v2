# =============================================================================
# feed-download.ps1 — motor genérico de feed planilha→vault (feed-planilha-vault)
#
# NÃO EDITE este arquivo por projeto. Tudo que varia mora em feed-config.json
# (ao lado). Assim o script é copiado byte-a-byte (BOM preservado) e nunca passa
# por editor que corrompa o encoding — causa-raiz de bug no PowerShell 5.1.
#
# Padrão base-completa: 1 arquivo de nome fixo por aba, SOBRESCRITO.
# Trava de segurança: baixa .tmp -> valida -> só então Move-Item por cima.
# Fonte com erro nunca destrói dado bom (loga WARN).
# =============================================================================
param([string]$ConfigPath = (Join-Path $PSScriptRoot 'feed-config.json'))

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

if (-not (Test-Path $ConfigPath)) { throw "feed-config.json não encontrado em $ConfigPath" }
$cfg     = Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
$DestDir  = Split-Path $ConfigPath -Parent
$LogFile  = Join-Path $DestDir '_download.log'
$MinBytes = if ($cfg.minBytes)     { [int]$cfg.minBytes }       else { 500 }
$MinRatio = if ($cfg.minLineRatio) { [double]$cfg.minLineRatio } else { 0.5 }

function Write-Log($Level, $Msg) {
    $line = "{0} [{1}] {2}" -f (Get-Date).ToString('yyyy-MM-dd HH:mm:ss'), $Level, $Msg
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    Write-Host $line
}

Write-Log 'INFO' '--- Início da atualização ---'

foreach ($t in $cfg.targets) {
    $outPath = Join-Path $DestDir $t.out
    $tmpPath = "$outPath.tmp"
    # Endpoints candidatos em ordem de preferência (R10 + fallback automático R2):
    #  1) /export?gid  — materializa fórmulas QUERY/IMPORTRANGE (o gviz TRUNCA). Preferencial quando há gid.
    #  2) gviz?gid     — fallback automático se /export for bloqueado: orgs Google Workspace
    #                    devolvem HTTP 401/403 anônimo no /export mesmo com a planilha pública
    #                    ("qualquer pessoa com o link") — gviz continua acessível. Sem fórmula, não trunca.
    #  3) gviz?sheet   — quando o target não tem gid (aba estática). Gids via .../htmlview ou #gid= na URL.
    $candidates = @()
    if ($t.gid) {
        $candidates += @{ label = 'export?gid'; url = "https://docs.google.com/spreadsheets/d/$($cfg.sheetId)/export?format=csv&gid=$($t.gid)" }
        $candidates += @{ label = 'gviz?gid';   url = "https://docs.google.com/spreadsheets/d/$($cfg.sheetId)/gviz/tq?tqx=out:csv&gid=$($t.gid)" }
    } else {
        $sheetEnc = [uri]::EscapeDataString($t.sheet)
        $candidates += @{ label = 'gviz?sheet'; url = "https://docs.google.com/spreadsheets/d/$($cfg.sheetId)/gviz/tq?tqx=out:csv&sheet=$sheetEnc" }
    }

    try {
        # curl.exe (R9): streaming pra disco, SEM o timeout oculto de 100s do
        # System.Net.WebClient que estoura em aba grande (gviz lento server-side),
        # e preserva UTF-8 cru. --fail => HTTP >=400 vira erro; -w captura o HTTP code.
        # Tenta cada endpoint na ordem; cai pro próximo se o atual falhar (ex: 401 no /export).
        $downloaded = $false
        $lastErr = ''
        foreach ($c in $candidates) {
            $httpCode = & curl.exe -sL --fail --max-time 600 -w '%{http_code}' $c.url -o $tmpPath
            if ($LASTEXITCODE -eq 0) {
                if ($c.label -ne $candidates[0].label) {
                    Write-Log 'INFO' "$($t.out): endpoint '$($candidates[0].label)' indisponível — fallback automático p/ '$($c.label)'."
                }
                $downloaded = $true
                break
            }
            $lastErr = "endpoint '$($c.label)' falhou (curl exit $LASTEXITCODE, HTTP $httpCode)"
            if (Test-Path $tmpPath) { Remove-Item $tmpPath -Force -ErrorAction SilentlyContinue }
        }
        if (-not $downloaded) { throw "$lastErr — nenhum endpoint disponível. Abortado." }

        $size = (Get-Item $tmpPath).Length
        if ($size -lt $MinBytes) {
            throw "baixado muito pequeno ($size bytes) — provável erro/login. Abortado."
        }

        $firstLine = Get-Content $tmpPath -TotalCount 1 -Encoding UTF8
        if ($t.mustContain -and ($firstLine -notmatch [regex]::Escape($t.mustContain))) {
            throw "header sem âncora '$($t.mustContain)' — provável página de erro. Abortado."
        }

        $newLines = (Get-Content $tmpPath -Encoding UTF8 | Measure-Object -Line).Lines
        if (Test-Path $outPath) {
            $oldLines = (Get-Content $outPath -Encoding UTF8 | Measure-Object -Line).Lines
            if ($oldLines -gt 0 -and $newLines -lt ($oldLines * $MinRatio)) {
                throw "novo $newLines linhas vs. $oldLines atuais (< $([int]($MinRatio*100))%) — truncamento suspeito. Abortado."
            }
        }

        Move-Item -Path $tmpPath -Destination $outPath -Force
        Write-Log 'OK' "$($t.out) atualizado — $newLines linhas, $size bytes."
    }
    catch {
        if (Test-Path $tmpPath) { Remove-Item $tmpPath -Force -ErrorAction SilentlyContinue }
        Write-Log 'WARN' "$($t.out) NÃO atualizado: $($_.Exception.Message)"
    }
}

Write-Log 'INFO' '--- Fim da atualização ---'
