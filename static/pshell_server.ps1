# Wait for console to initialize
Start-Sleep -Milliseconds 500

# --- Win32 API to move window ---
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
}
"@

# --- Launch Windows Terminal with WSL ---
$wtPath = "C:\Users\<YourUser>\AppData\Local\Microsoft\WindowsApps\wt.exe"
$profile = "Ubuntu-24.04"
$tabTitle = "No Pasa Nada SERVER"

Start-Process $wtPath -ArgumentList "-p `"$profile`" --title `"$tabTitle`" bash -ic `"cd ~/NoPasaNadaPE/server && uv run main.py; exec bash`""

# Wait for WT to open
Start-Sleep -Milliseconds 1500

# --- Find WT window and move to secondary screen (middle third, lower half) ---
$hwnd = [Win32]::FindWindow("CASCADIA_HOSTING_WINDOW_CLASS", $tabTitle)
if ($hwnd -ne [IntPtr]::Zero) {
    Add-Type -AssemblyName System.Windows.Forms
    $bounds = [System.Windows.Forms.Screen]::AllScreens[1].Bounds

    $width  = [int]($bounds.Width / 3)      # middle third
    $height = [int]($bounds.Height / 2)     # lower half
    $x = $bounds.X + $width
    $y = $bounds.Y + $height

    [Win32]::MoveWindow($hwnd, $x, $y, $width, $height, $true) | Out-Null
} else {
    Write-Host "Windows Terminal server window not found."
}
