param(
  [string]$Python = (Join-Path (Split-Path $PSScriptRoot -Parent) '.venv\Scripts\python.exe'),
  [string]$WorkDir = (Join-Path $env:LOCALAPPDATA 'ChembrainPaperProcessor'),
  [switch]$Remove
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes($projectRoot.ToLowerInvariant()))
$identity = ([BitConverter]::ToString($hash)).Replace('-','').Substring(0,12)
$name = "Chembrain Paper Processor $identity"
if ($Remove) {
  if (Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $name -Confirm:$false }
  Write-Output 'Weekly paper processor removed.'
  exit
}
if (!(Test-Path -LiteralPath $Python -PathType Leaf)) { throw 'Install Python 3.12 and processor dependencies, or pass -Python with its full path. The browser app itself does not need Python.' }
$archive = [IO.Path]::GetFullPath($WorkDir)
if ($archive.StartsWith($projectRoot + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Use an archive directory outside the application repository.' }
New-Item -ItemType Directory -Force -Path $archive | Out-Null
$outputFile = Join-Path $archive 'library.json'
$arguments = '-m paper_pipeline weekly --work-dir "' + $archive + '" --out "' + $outputFile + '"'
$action = New-ScheduledTaskAction -Execute ([IO.Path]::GetFullPath($Python)) -Argument $arguments -WorkingDirectory $projectRoot
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At '09:00'
$user = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Write-Output "Weekly processor enabled: Monday 09:00, this PC's local time; keep the PC on, online and logged in."
Write-Output "Compact package: $outputFile. Import this file in the browser library."
