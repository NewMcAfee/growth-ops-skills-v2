# =============================================================================
# register-task.ps1 — registra (ou recria) a tarefa agendada do feed.
# Encapsula as flags de robustez que faltam num Register-ScheduledTask ingênuo:
#   -StartWhenAvailable      roda assim que possível se o PC estava desligado
#   -AllowStartIfOnBatteries CRÍTICO em laptop (sem isso, não roda na bateria)
#   -DontStopIfGoingOnBatteries  não mata a execução se cair pra bateria no meio
#   -RestartCount/-Interval  retry em falha transitória de rede
#
# Suporta 1+ horários no dia (um trigger diário por horário informado).
#
# Uso:
#   .\register-task.ps1 -TaskName "Feed - Cliente X" -ScriptPath "C:\...\motor.ps1" -Times 09:00
#   .\register-task.ps1 -TaskName "Feed - Cliente X" -ScriptPath "C:\...\motor.ps1" -Times 07:30,17:30
# =============================================================================
param(
    [Parameter(Mandatory)][string]$TaskName,
    [Parameter(Mandatory)][string]$ScriptPath,
    [string[]]$Times = @('09:00')
)
$ErrorActionPreference = 'Stop'

$action  = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
$triggers = @($Times | ForEach-Object { New-ScheduledTaskTrigger -Daily -At $_ })
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5) `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $triggers `
    -Settings $settings -Principal $principal `
    -Description "Feed planilha->vault. Baixa abas e sobrescreve CSV. Gerado por feed-planilha-vault." `
    -Force | Out-Null

$info = Get-ScheduledTaskInfo -TaskName $TaskName
Write-Host "Tarefa '$TaskName' registrada ($($Times -join ', ')). Próxima execução: $($info.NextRunTime)"
