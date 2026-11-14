param(
    [string]$Docx = (Join-Path $PSScriptRoot '..\docs\report\Candidate_Lab_Project_Report.docx'),
    [string]$Pdf = (Join-Path $PSScriptRoot '..\docs\report\Candidate_Lab_Project_Report.pdf')
)

$ErrorActionPreference = 'Stop'
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.ScreenUpdating = $false

    $document = $word.Documents.Open($Docx, $false, $false)
    $document.Fields.Update() | Out-Null
    foreach ($toc in $document.TablesOfContents) {
        $toc.Update() | Out-Null
    }
    $document.Repaginate()
    $document.Save()

    # 17 = wdExportFormatPDF, 0 = wdExportDocumentContent
    $document.ExportAsFixedFormat(
        $Pdf, 17, $false, 0, 0, 0, 0, 0,
        $true, $true, 0, $true, $true, $false
    ) | Out-Null

    $pageCount = $document.ComputeStatistics(2)
    Write-Output "Exported: $Pdf"
    Write-Output "Pages: $pageCount"
}
finally {
    if ($document -ne $null) {
        $document.Close($false)
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($document) | Out-Null
    }
    if ($word -ne $null) {
        $word.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
