# Grabs a window at full resolution without focusing it (PrintWindow with
# PW_RENDERFULLCONTENT, so a DirectX viewport is drawn), for store art taken in
# the game (night brief 2026-10-26 step 6; blender/_review_launch/README.md).
#
#   powershell -File tools/capture_window.ps1 -ProcessId 17220 -Out shot.png
#
# The window must not be minimised. Crop and scale afterwards (Python/PIL).
param([int]$ProcessId, [string]$Out)

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class Grab {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
}
"@

$p = Get-Process -Id $ProcessId
$h = $p.MainWindowHandle
$r = New-Object Grab+RECT
[void][Grab]::GetWindowRect($h, [ref]$r)
$w = $r.R - $r.L; $ht = $r.B - $r.T
$bmp = New-Object System.Drawing.Bitmap $w, $ht
$g = [System.Drawing.Graphics]::FromImage($bmp)
$dc = $g.GetHdc()
[void][Grab]::PrintWindow($h, $dc, 2)
$g.ReleaseHdc($dc)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"$w x $ht -> $Out"
