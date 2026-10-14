# One parallel DeepSeek DRAFTER (HERMES_DRAFTER.md). Several can run at once: each gets its own worktree
# private\worktrees\ds-<Batch> and never touches the main checkout, so make compare / merges stay free.
#   powershell -ExecutionPolicy Bypass -File ops\deepseek-draft.ps1 -Batch b9a -List D:\...\names.txt
# Stops before starting if DeepSeek spend >= $BudgetStopUsd. Done when private\drafts\report_<Batch>.md exists.
param([Parameter(Mandatory)][string]$Batch, [Parameter(Mandatory)][string]$List,
      [ValidateSet('low','medium','high')][string]$Reasoning = 'medium', [int]$MaxNudges = 2)
. "$PSScriptRoot\common.ps1"
$log = "$Logs\deepseek-draft-$Batch.log"
$report = "$Repo\private\drafts\report_$Batch.md"
function Say($s) { Write-Host $s -ForegroundColor Cyan; $s | Out-File $log -Append -Encoding utf8 }

$spent = Get-DeepSeekSpend
Say "=== DeepSeek drafter $Batch  $(Get-Date -Format s)  spent so far `$$('{0:N2}' -f $spent) of `$$BudgetStopUsd ==="
if ($spent -ge $BudgetStopUsd) { Say 'BUDGET STOP: DeepSeek spend reached the limit. Ask Matter_Scatter.'; exit 3 }

$wt = "$Repo\private\worktrees\ds-$Batch"
if (-not (Test-Path $wt)) { git -C $Repo worktree add -q --detach $wt main 2>&1 | Out-Null }
$names = (Get-Content -LiteralPath $List -Raw).Trim() -replace '\s+', ' '
# No double quotes inside prompts (PowerShell 5.1 splits native args at embedded quotes).
$p = "You are Hermes on DeepSeek, a parallel DRAFTER for Yugioh_DeComp_V2, batch $Batch. Your worktree is $wt. " +
     "Read D:\Yugioh_DeComp_V2\HERMES_DRAFTER.md and do exactly that for these functions: $names . " +
     "You are done when $report is written."
$nudge = "Continue drafter batch $Batch. Your last message had no tool call. Make the next tool call now; you are done " +
         "only when $report is written."
$t0 = Get-UnixNow
& $Hermes -z $p --provider deepseek -m $DeepSeekModel --reasoning $Reasoning -t 'terminal,file,todo' --in $wt 2>&1 |
    Tee-Object -FilePath $log -Append
$sid = Get-NewestSession $wt $t0
for ($n = 1; $n -le $MaxNudges -and -not (Test-Path $report) -and $sid; $n++) {
    Say "--- nudge $n (resume $sid)"
    & $Hermes -z $nudge --provider deepseek -m $DeepSeekModel --reasoning $Reasoning -t 'terminal,file,todo' --in $wt --resume $sid 2>&1 |
        Tee-Object -FilePath $log -Append
}
$after = Get-DeepSeekSpend
Say "=== done: report=$(Test-Path $report) session=$sid cost so far `$$('{0:N2}' -f ($after - $spent)) total `$$('{0:N2}' -f $after) ==="
