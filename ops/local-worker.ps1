# 24/7 local job runner. Run it in the Claude app's "Local worker" terminal tab:
#   powershell -ExecutionPolicy Bypass -File D:\Yugioh_DeComp_V2\ops\local-worker.ps1
# Takes private\jobs\queue\*.json oldest first. Each job runs in its own git worktree on branch local/<id>.
# The WORKER (not the model) decides pass/fail: job check command + allowed paths + repo guard + ROM hash.
# Pause: create the file private\jobs\STOP (delete it to resume). Ctrl+C stops the loop.
param([int]$MaxNudges = 4, [int]$IdleSeconds = 60, [switch]$Once)   # -Once: run at most one job, then exit
. "$PSScriptRoot\common.ps1"

function Say($s, $c = 'Gray') { Write-Host "[$(Get-Date -Format HH:mm:ss)] $s" -ForegroundColor $c }
function Save($job, $path) { $job | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $path -Encoding utf8 }
function Run-Bash($cwd, $cmd) {
    Push-Location $cwd
    try { $out = & $Bash -lc $cmd 2>&1 | Out-String; $code = $LASTEXITCODE } finally { Pop-Location }
    [pscustomobject]@{ code = $code; out = $out }
}

Say "local worker started (model $LocalModel). Queue: $Jobs\queue" 'Green'
while ($true) {
    if (Test-Path "$Jobs\STOP") { Say 'paused (private\jobs\STOP exists)' 'Yellow'; Start-Sleep $IdleSeconds; continue }
    $file = Get-ChildItem "$Jobs\queue" -Filter *.json -ErrorAction SilentlyContinue | Sort-Object Name | Select -First 1
    if (-not $file) { if ($Once) { Say 'queue empty'; break }; Start-Sleep $IdleSeconds; continue }

    $job  = Get-Content -LiteralPath $file.FullName -Raw -Encoding utf8 | ConvertFrom-Json
    $id   = $job.id
    $run  = "$Jobs\running\$id.json"
    Move-Item -LiteralPath $file.FullName $run -Force
    $attempt = [int]($job.attempts) + 1
    $job | Add-Member -Force attempts $attempt
    Say "=== $id (attempt $attempt): $($job.title)" 'Cyan'

    # Worktree from main (reused on a retry).
    $wt = "$Repo\private\worktrees\$id"
    if (-not (Test-Path $wt)) {
        git -C $Repo worktree add -q $wt -b "local/$id" main 2>&1 | Out-Null
        if (-not (Test-Path $wt)) { git -C $Repo worktree add -q $wt "local/$id" 2>&1 | Out-Null }
    }
    # Read-only ROM copy so repo tools that use ROOT/private/baserom.gba work in the worktree.
    $wtRom = "$wt\private\baserom.gba"
    if (-not (Test-Path $wtRom)) {
        New-Item -ItemType Directory -Force "$wt\private" | Out-Null
        Copy-Item "$Repo\private\baserom.gba" $wtRom; (Get-Item $wtRom).IsReadOnly = $true
    }
    $job | ConvertTo-Json -Depth 6 | Set-Content "$wt\JOB.json" -Encoding utf8
    $log = "$Logs\job-$id-a$attempt.log"

    $p = "You are the local worker on Yugioh_DeComp_V2. Your folder is $wt (a git worktree on branch local/$id). " +
         "Read $wt\LOCAL_WORKER.md, then $wt\JOB.json, and do exactly that job inside $wt only. Change only the " +
         "files listed in allowed_paths. Run the check command yourself, fix until it passes, commit on your branch, " +
         "then write $wt\RESULT.md. Every message must contain a tool call until RESULT.md is written."
    $nudge = "Continue job $id. Your last message had no tool call. Make the next tool call now; you are done only " +
             "when the check passes, your work is committed and $wt\RESULT.md is written."
    # Snapshot the main checkout: a job must not leave files there (the model sometimes writes to
    # D:\Yugioh_DeComp_V2\src instead of its worktree).
    $mainBefore = @(git -C $Repo status --porcelain --untracked-files=all 2>$null)
    $t0 = Get-UnixNow
    & $Hermes -z $p -m $LocalModel -t terminal,file,todo --in $wt 2>&1 | Out-File $log -Encoding utf8
    $sid = Get-NewestSession $wt $t0
    for ($n = 1; $n -le $MaxNudges -and $sid -and -not (Test-Path "$wt\RESULT.md"); $n++) {
        Say "   nudge $n" 'DarkGray'
        & $Hermes -z $nudge -m $LocalModel -t terminal,file,todo --in $wt --resume $sid 2>&1 | Out-File $log -Append -Encoding utf8
    }

    # Judge (never trust the model's own claims).
    $check   = Run-Bash $wt $job.check
    $changed = @(git -C $wt diff --name-only --merge-base main 2>$null) + @(git -C $wt ls-files --others --exclude-standard 2>$null) |
               Where-Object { $_ -and $_ -ne 'RESULT.md' } | Sort-Object -Unique
    $allowed = @($job.allowed_paths)
    $bad     = @($changed | Where-Object { $f = $_; -not ($allowed | Where-Object { $f -like $_ }) })
    # Only the job's own allowed paths count as strays (DeepSeek may be creating other files there).
    $strays  = @(git -C $Repo status --porcelain --untracked-files=all 2>$null | Where-Object {
                   $l = $_; $mainBefore -notcontains $l -and $l -like '`?`? *' -and
                   ($allowed | Where-Object { $l.Substring(3) -like $_ }) })
    foreach ($s in $strays) {
        $p = $s.Substring(3); $q = "$Repo\private\quarantine"; New-Item -ItemType Directory -Force $q | Out-Null
        Move-Item -LiteralPath "$Repo\$p" "$q\$id-$($p -replace '[\\/]', '_')" -Force
        $bad += "MAIN:$p"
    }
    $dirty   = @(git -C $wt status --porcelain 2>$null | Where-Object { $_ -notmatch 'RESULT.md|JOB.json' })
    $guard   = & $Py -I "$Repo\tools\guard_repo.py" --repo $wt 2>&1 | Out-String; $guardOk = ($LASTEXITCODE -eq 0)
    & $Py -I "$Repo\tools\hash_rom.py" | Out-Null
    $romOk = ($LASTEXITCODE -eq 0) -and ((Get-FileHash $wtRom -Algorithm SHA1).Hash -eq 'D3710031520D9CDAE70D870C60B1667285FE5230')
    $pass = ($check.code -eq 0) -and ($bad.Count -eq 0) -and ($dirty.Count -eq 0) -and $guardOk -and $romOk -and ($changed.Count -gt 0)

    $tail = ($check.out -split "`n" | Select -Last 25) -join "`n"
    $job | Add-Member -Force last_result ([ordered]@{
        time = (Get-Date -Format s); session = $sid; pass = $pass; check_exit = $check.code; check_tail = $tail
        changed = $changed; outside_allowed = $bad; uncommitted = $dirty; guard_ok = $guardOk; rom_ok = $romOk
        commit = (git -C $wt rev-parse --short HEAD); log = $log })
    if (-not $romOk) { Say 'ROM HASH CHANGED - stopping worker. Tell Claude.' 'Red'; Save $job $run; New-Item "$Jobs\STOP" -Force | Out-Null; continue }
    if ($pass) {
        $job | Add-Member -Force status 'passed-awaiting-critics'
        Save $job "$Jobs\passed\$id.json"; Remove-Item -LiteralPath $run
        Say "   PASS $id  (changed: $($changed -join ', '))" 'Green'
    } elseif ($attempt -lt [int]($job.max_attempts)) {
        Save $job "$Jobs\queue\$id.json"; Remove-Item -LiteralPath $run
        Say "   FAIL $id - requeued (check exit $($check.code); outside allowed: $($bad -join ', '))" 'Yellow'
    } else {
        $job | Add-Member -Force status 'failed-for-deepseek'
        Save $job "$Jobs\failed\$id.json"; Remove-Item -LiteralPath $run
        Say "   FAIL $id - out of attempts, handed back to DeepSeek" 'Red'
    }
    if ($Once) { break }
}
