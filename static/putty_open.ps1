$puttyPath = "C:\Program Files\PuTTY\putty.exe"
$sessionName = "Google Cloud VM"

Start-Process $puttyPath -ArgumentList "-load `"$sessionName`""

# Wait for PuTTY window
Start-Sleep -Milliseconds 1000

# --- Move PuTTY to secondary screen, lower-left third ---
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

$hwnd = [Win32]::FindWindow("PuTTY", $sessionName)
if ($hwnd -ne [IntPtr]::Zero) {
    Add-Type -AssemblyName System.Windows.Forms
    $bounds = [System.Windows.Forms.Screen]::AllScreens[1].Bounds

    $width  = [int]($bounds.Width / 3)       # left third
    $height = [int]($bounds.Height / 2)      # lower half
    $x = $bounds.X
    $y = $bounds.Y + $height

    [Win32]::MoveWindow($hwnd, $x, $y, $width, $height, $true) | Out-Null
} else {
    Write-Host "PuTTY window not found."
}
