# One DeepSeek Flash turn of Hermes on TASK [Entry]. Run it in the Claude app's "DeepSeek" terminal tab.
#   powershell -ExecutionPolicy Bypass -File D:\Yugioh_DeComp_V2\ops\deepseek-turn.ps1 -Entry 001 [-Reasoning low]
# Stops before starting if V2 DeepSeek spend >= $BudgetStopUsd. Resumes the same session (by exact id) with a
# nudge if the model ends without its REPORT, at most -MaxNudges times.
param([Parameter(Mandatory)][string]$Entry, [ValidateSet('low','medium','high')][string]$Reasoning = 'medium',
      [int]$MaxNudges = 2, [switch]$Ghidra)   # -Ghidra: give this turn the ghidra-mcp tools (toolset 'ghidra')
. "$PSScriptRoot\common.ps1"
$HermesCfg = 'C:\Users\USER\AppData\Local\hermes\config.yaml'
# ghidra-mcp is "enabled: false" in Hermes's config by default: with the server down every Hermes session would
# wait 15 s for it. -Ghidra starts the server, flips the flag for this turn only, and always flips it back.
function Set-GhidraMcp([bool]$on) {
    $txt = [IO.File]::ReadAllText($HermesCfg)
    $new = [regex]::Replace($txt, '(?ms)(^  ghidra:\r?\n(?:    .*\r?\n)*?    enabled: )(true|false)', ('${1}' + ($(if ($on) { 'true' } else { 'false' }))))
    if ($new -ne $txt) { [IO.File]::WriteAllText($HermesCfg, $new) }
}
$Tools = 'terminal,file,todo'
if ($Ghidra) {
    wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/ghidra_mcp_server.sh start | Out-Null
    Set-GhidraMcp $true
    $Tools = 'terminal,file,todo,ghidra'   # hermes -z takes the MCP server name (oneshot.py), not mcp-<name>
}
$next = '{0:D3}' -f ([int]$Entry + 1)
$log  = "$Logs\deepseek-$Entry.log"
function HasReport { Select-String -LiteralPath $Conv -Pattern "^## \[$next\] (DeepSeek|Hermes)" -Quiet }
function Say($s) { Write-Host $s -ForegroundColor Cyan; $s | Out-File $log -Append -Encoding utf8 }

$spent = Get-DeepSeekSpend
Say "=== DeepSeek turn $Entry  $(Get-Date -Format s)  spent so far `$$('{0:N2}' -f $spent) of `$$BudgetStopUsd ==="
if ($spent -ge $BudgetStopUsd) { Say 'BUDGET STOP: DeepSeek spend reached the limit. Ask Matter_Scatter.'; exit 3 }
$bal = Get-DeepSeekBalance
if ($bal -ge 0 -and $bal -lt $MinBalanceUsd) { Say "BUDGET STOP: DeepSeek balance is `$$bal (< `$$MinBalanceUsd). Ask Matter_Scatter."; exit 3 }

# No double quotes inside prompts (PowerShell 5.1 splits native args at embedded quotes).
$p = "You are Hermes on DeepSeek, the main engineer of Yugioh_DeComp_V2. Read D:\Yugioh_DeComp_V2\HERMES_START.md " +
     "and D:\Yugioh_DeComp_V2\AGENTS.md, then entry [$Entry] at the end of D:\Yugioh_DeComp_V2\AI_Conversation.md, " +
     "and do exactly that TASK. Finish by appending REPORT entry [$next] and committing, as HERMES_START.md describes."
$nudge = "Continue TASK [$Entry]. Your last message had no tool call. Make the next tool call now; you are done " +
         "only when REPORT [$next] is appended to D:\Yugioh_DeComp_V2\AI_Conversation.md and committed."
$t0 = Get-UnixNow
try {
    & $Hermes -z $p --provider deepseek -m $DeepSeekModel --reasoning $Reasoning -t $Tools --in $Repo 2>&1 |
        Tee-Object -FilePath $log -Append
    $sid = Get-NewestSession $Repo $t0
    for ($n = 1; $n -le $MaxNudges -and -not (HasReport) -and $sid; $n++) {
        Say "--- nudge $n (resume $sid)"
        & $Hermes -z $nudge --provider deepseek -m $DeepSeekModel --reasoning $Reasoning -t $Tools --in $Repo --resume $sid 2>&1 |
            Tee-Object -FilePath $log -Append
    }
} finally {
    if ($Ghidra) {
        Set-GhidraMcp $false
        wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/ghidra_mcp_server.sh stop | Out-Null
    }
}
$after = Get-DeepSeekSpend
Say "=== done: report=$(HasReport) session=$sid turn cost `$$('{0:N2}' -f ($after - $spent)) total `$$('{0:N2}' -f $after) ==="
