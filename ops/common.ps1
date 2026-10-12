# Shared settings for the ops scripts. Dot-source it:  . D:\Yugioh_DeComp_V2\ops\common.ps1
$Repo        = 'D:\Yugioh_DeComp_V2'
$Hermes      = 'C:\Users\USER\AppData\Local\hermes\bin\hermes.exe'
$Py          = 'C:\Users\USER\AppData\Local\hermes\hermes-agent\.hermes-runtime\python\cpython-3.11-windows-x86_64-none\python.exe'
$Bash        = 'C:\Users\USER\AppData\Local\hermes\git\bin\bash.exe'   # Git Bash bundled with Hermes
$Conv        = "$Repo\AI_Conversation.md"
$Logs        = "$Repo\private\logs"
$Jobs        = "$Repo\private\jobs"
$DeepSeekModel    = 'deepseek-v4-flash-vision-exp'   # billed as "deepseek-flash" (Matter_Scatter: Flash only)
$LocalModel       = 'qwen36-agent'                   # Ollama: huihui qwen3.6 abliterated 35B-A3B, tuned sampler
$BudgetStart      = '2026-10-12T05:40'               # V2 budget window starts here (all DeepSeek use counts)
$BudgetStopUsd    = 30.0                             # hard stop; $5 of the $35 balance stays in reserve
New-Item -ItemType Directory -Force $Logs | Out-Null

function Get-DeepSeekSpend {
    $j = & $Py -I "$Repo\tools\deepseek_spend.py" --since $BudgetStart --json | ConvertFrom-Json
    [double]$j.cost_usd
}
function Get-NewestSession([string]$Cwd, [double]$After = 0) {
    (& $Py -I "$Repo\tools\newest_session.py" $Cwd --after $After | Out-String).Trim()
}
function Get-UnixNow { [double](([DateTimeOffset]::UtcNow).ToUnixTimeSeconds()) }
