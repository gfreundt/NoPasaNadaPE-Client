# Wait for console window to initialize
Start-Sleep -Milliseconds 500

# --- Window setup ---
$Host.UI.RawUI.WindowTitle = "No Pasa Nada CLIENT"
$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "Green"
Clear-Host

# --- Resize console buffer size ---
$rawUI = $Host.UI.RawUI
$size = $rawUI.WindowSize
$size.Width = 120
$size.Height = 30
$rawUI.WindowSize = $size

$buffer = $rawUI.BufferSize
if ($buffer.Width -lt $size.Width) {
    $buffer.Width = $size.Width
    $rawUI.BufferSize = $buffer
}
$rawUI.WindowSize = $size

# --- Win32 API for window manipulation & screen detection ---
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;

public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
}
"@ -ReferencedAssemblies "System.Windows.Forms"

# Get window handle
$hWnd = [Win32]::GetForegroundWindow()

# Get all screens
$screens = [System.Windows.Forms.Screen]::AllScreens

if ($screens.Count -gt 1) {
    # Use the secondary screen
    $bounds = $screens[1].Bounds

    # --- Calculate lower half, right third ---
    $width  = [int]($bounds.Width / 3)    # one third of screen
    $height = [int]($bounds.Height / 2)  # lower half
    $x = $bounds.X + (2 * $width)        # start at 2/3 across (rightmost third)
    $y = $bounds.Y + $height             # start halfway down

    # Move console window
    [Win32]::MoveWindow($hWnd, $x, $y, $width, $height, $true) | Out-Null
}

# --- Change directory and run command ---
Set-Location "D:\pythonCode\NoPasaNadaPE\client"
uv run main.py
