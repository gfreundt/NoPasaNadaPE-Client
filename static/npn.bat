@echo off
:: --- Launch client PS1 ---
start "" powershell -ExecutionPolicy Bypass -NoExit -File "D:\pythonCode\NoPasaNadaPE\client\static\pshell_client.ps1"

:: Wait 2 seconds for the window to initialize
timeout /t 2 /nobreak >nul

:: --- Launch server in WSL via Windows Terminal ---
start "" powershell -ExecutionPolicy Bypass -NoProfile -File "D:\pythonCode\NoPasaNadaPE\client\static\pshell_server_wt.ps1"

:: Wait 2 seconds for the window to initialize
timeout /t 2 /nobreak >nul

:: --- Launch PuTTY ---
start "" powershell -ExecutionPolicy Bypass -NoProfile -File "D:\pythonCode\NoPasaNadaPE\client\static\putty_open.ps1"

exit
