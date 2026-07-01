$wshell = New-Object -ComObject wscript.shell;
$chromes = Get-Process chrome -ErrorAction SilentlyContinue;
$target = $null;

foreach ($p in $chromes) {
    try {
        $procInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $($p.Id)" -ErrorAction SilentlyContinue;
        if ($procInfo -and $procInfo.CommandLine -like "*chrome_profile*") {
            $target = $p;
            break;
        }
    } catch {}
}

if ($target) {
    $wshell.AppActivate($target.Id);
    Write-Host "Chrome window activated successfully! (PID: $($target.Id))";
} else {
    Write-Host "No Chrome window found with matching profile paths.";
}
