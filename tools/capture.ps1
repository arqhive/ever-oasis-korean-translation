param([int]$Pid_, [string]$Out)
Add-Type @"
using System;using System.Runtime.InteropServices;using System.Drawing;
public class Cap {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  public struct RECT { public int L,T,R,B; }
  public static void Shot(IntPtr h, string path){
    ShowWindow(h,9); SetForegroundWindow(h); System.Threading.Thread.Sleep(700);
    RECT r; GetWindowRect(h, out r);
    int w=r.R-r.L, ht=r.B-r.T;
    var bmp=new Bitmap(w,ht);
    using(var g=Graphics.FromImage(bmp)) g.CopyFromScreen(r.L,r.T,0,0,new Size(w,ht));
    bmp.Save(path, System.Drawing.Imaging.ImageFormat.Png);
  }
}
"@ -ReferencedAssemblies System.Drawing,System.Windows.Forms
$p=Get-Process -Id $Pid_
[Cap]::Shot($p.MainWindowHandle,$Out)
Write-Output "saved $Out"
