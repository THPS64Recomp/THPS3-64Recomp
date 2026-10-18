# One command on Windows 10/11 x64: your ROM -> generated C -> native THPS3 host (D3D12 via RT64).
#
#   powershell -ExecutionPolicy Bypass -File tools\build_windows.ps1 -Rom "C:\roms\<your THPS3 dump>.z64"
#   powershell -ExecutionPolicy Bypass -File tools\build_windows.ps1 -Stub     # no ROM: toolchain check only
#
# A thin wrapper: the script is shared by the THPS recomp hosts (decomp\common\host\tools\build_windows.ps1) and takes the same
# parameters (several ROMs: -Rom "a","b"). Details: README.md ("Windows and Linux"), docs\WINDOWS-TEST.md.
param(
    [string[]]$Rom = @(),
    [switch]$Stub,
    [switch]$Split,
    [switch]$OwnSdl2,
    [string]$BuildType = "RelWithDebInfo",
    [switch]$Clean
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:THPS_HOST = Split-Path -Parent $here
# The shared host tree: $env:THPS_HOST_ROOT (an override), else decomp\common (a directory here, the THPS64Host submodule in a game repository).
if (-not $env:THPS_HOST_ROOT) {
    $c = Join-Path $env:THPS_HOST "..\..\common"
    if (Test-Path (Join-Path $c "host\tools\hostenv.py")) { $env:THPS_HOST_ROOT = (Resolve-Path $c).Path }
}
if (-not $env:THPS_HOST_ROOT -or -not (Test-Path (Join-Path $env:THPS_HOST_ROOT "host\tools\hostenv.py"))) {
    throw "the shared host (THPS64Host) was not found: git submodule update --init, or set THPS_HOST_ROOT"
}
$shared = Join-Path $env:THPS_HOST_ROOT "host\tools\build_windows.ps1"
& $shared @PSBoundParameters
exit $LASTEXITCODE
