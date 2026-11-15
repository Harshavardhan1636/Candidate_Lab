param(
    [string[]]$Editions = @('standard', 'detailed'),
    [string]$Suffix = ''
)

$ErrorActionPreference = 'Stop'
$reportDir = Join-Path $PSScriptRoot '..\docs\report'
$word = $null
$document = $null

function Export-Edition {
    param(
        [string]$Edition,
        [string]$Docx,
        [string]$Pdf
    )

    $script:document = $word.Documents.Open($Docx, $false, $false)
    $script:document.Fields.Update() | Out-Null
    foreach ($toc in $script:document.TablesOfContents) {
        $toc.Update() | Out-Null
    }

    # Word regenerates the built-in TOC styles; compact them so the TOC fits one page.
    foreach ($name in @('toc 1', 'toc 2')) {
        try {
            $style = $script:document.Styles.Item($name)
            $style.ParagraphFormat.SpaceBefore = 0
            $style.ParagraphFormat.SpaceAfter = 2
            $style.ParagraphFormat.LineSpacingRule = 0
            if ($name -eq 'toc 2') {
                $style.ParagraphFormat.LeftIndent = 15.6
            }
            else {
                $style.ParagraphFormat.LeftIndent = 0
            }
            $style.ParagraphFormat.FirstLineIndent = 0
        }
        catch {
            Write-Warning "TOC style '$name' was not found."
        }
    }
    $script:document.Repaginate()
    $script:document.Save()

    # 17 = wdExportFormatPDF, 0 = wdExportDocumentContent
    $script:document.ExportAsFixedFormat(
        $Pdf, 17, $false, 0, 0, 0, 0, 0,
        $true, $true, 0, $true, $true, $false
    ) | Out-Null

    $pageCount = $script:document.ComputeStatistics(2)
    Write-Output ("{0}: {1} pages -> {2}" -f $Edition, $pageCount, $Pdf)
    $script:document.Close($false)
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($script:document) | Out-Null
    $script:document = $null
}

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.ScreenUpdating = $false

    foreach ($edition in $Editions) {
        $editionName = (Get-Culture).TextInfo.ToTitleCase($edition)
        $docx = Join-Path $reportDir "Candidate_Lab_Project_Report_$editionName$Suffix.docx"
        $pdf = Join-Path $reportDir "Candidate_Lab_Project_Report_$editionName$Suffix.pdf"
        if (-not (Test-Path -LiteralPath $docx)) {
            throw "Missing report document: $docx"
        }
        Export-Edition -Edition $editionName -Docx $docx -Pdf $pdf
    }
}
finally {
    if ($script:document -ne $null) {
        $script:document.Close($false)
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($script:document) | Out-Null
    }
    if ($word -ne $null) {
        $word.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
