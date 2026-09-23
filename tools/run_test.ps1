param([string]$Out,[int]$Wait=55)
Get-Process azahar -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 2
$exe = "C:\Users\hgyst\az\azahar.exe"
$cxi = "C:\Users\hgyst\eo\emu\EverOasis_JP.cxi"
$cap = "C:\Users\hgyst\eo\tools\capture.ps1"
$p = Start-Process -FilePath $exe -ArgumentList ('"' + $cxi + '"') -PassThru
Start-Sleep $Wait
& powershell -ExecutionPolicy Bypass -File $cap -Pid_ $p.Id -Out $Out
Stop-Process -Id $p.Id -Force
