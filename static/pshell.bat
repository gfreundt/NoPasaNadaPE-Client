@echo off
:: Run pshell.ps1 in its own PowerShell window
start "" powershell -ExecutionPolicy Bypass -NoExit -File "D:\pythonCode\NoPasaNadaPE\client\static\pshell_client.ps1"

:: Wait 2 seconds before launching the server
timeout /t 2 /nobreak >nul

:: Run pshell2.ps1 in its own PowerShell window
start "" powershell -ExecutionPolicy Bypass -NoExit -File "D:\pythonCode\NoPasaNadaPE\client\static\pshell_server.ps1"

timeout /t 2 /nobreak >nul

:: Run PuTTY and move it using PowerShell
start "" powershell -ExecutionPolicy Bypass -NoProfile -File "D:\pythonCode\NoPasaNadaPE\client\static\putty_open.ps1"

exit
