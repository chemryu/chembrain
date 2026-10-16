param(
    [string]$Root = 'C:\Users\Ren Lab\Box\AIWorkflow\ChemBrainProject'
)
$ErrorActionPreference = 'Stop'
$exe = Join-Path $PSScriptRoot 'ChembrainWorkflow.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw 'Extract the complete ZIP first.' }
& $exe install --root $Root
if ($LASTEXITCODE -ne 0) { throw 'Folder installation failed.' }
