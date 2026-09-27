# 과정안 hwpx → PDF (한글이 설치된 윈도에서만)
#   powershell -ExecutionPolicy Bypass -File _tools\hwpx2pdf.ps1 -Src "<hwpx 폴더>" -Out assets\pdf
param([string]$Src, [string]$Out)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force $Out | Out-Null
$OutFull = (Resolve-Path $Out).Path
$hwp = New-Object -ComObject HWPFrame.HwpObject
try { $hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule') | Out-Null } catch {}
$hwp.XHwpWindows.Item(0).Visible = $false
Get-ChildItem -LiteralPath $Src -Filter 'B*.hwpx' | Sort-Object Name | ForEach-Object {
  $code = $_.Name.Substring(0, 3)
  $dst = Join-Path $OutFull ($code + '.pdf')
  $hwp.Open($_.FullName, 'HWPX', 'forceopen:true') | Out-Null
  $hwp.SaveAs($dst, 'PDF', '') | Out-Null
  $hwp.Clear(1)
  Write-Output "$code -> $dst"
}
$hwp.Quit()
