@echo off
setlocal

if not exist "Su.exe.exe" (
  echo [ERROR] Su.exe.exe not found in current folder.
  echo Please place this BAT file in the same folder as Su.exe.exe or run from repo root.
  exit /b 1
)

echo Starting portable app (no Python install needed)...
start "MSP Portable" "Su.exe.exe"

endlocal
