Sub extract_scatter_chart()
Dim filepath As String

    MsgBox "Opening: U:\04 Data and tools\Reports\scoreboard\Pivot_for_Scatters.xlsm", vbInformation, "Info"
    Workbooks.Open Filename:="U:\04 Data and tools\Reports\scoreboard\Pivot_for_Scatters.xlsm"
    Workbooks("Pivot_for_Scatters.xlsm").Activate
    filepath = Workbooks("Scoreboard macros.xlsm").Sheets(1).Range("B20").Value
    filepath = Replace(filepath, "dissemination", "output")
    Dim response As VbMsgBoxResult
    response = MsgBox("Have you updated the path of the 'Text SCATTER' data source in PowerPivot in Pivot_for_Scatters.xlsm?" & vbNewLine & _
                  "The new path should be:" & vbNewLine & filepath & "SCATTER.csv" & vbNewLine & vbNewLine & _
                  "If not, click now 'No' to stop this macro and go to the PowerPivot tab in Pivot_for_Scatters.xlsm, click on the green " & _
                  "button 'Manage', then click on 'Existing connections' and update the path. In PowerPivot's 'Edit Connection' dialog " & _
                  "window make sure to tick 'Use first row as column headers' before clicking 'Save'." & _
                  vbNewLine & "Warning: running this macro further takes a lot of time, be patient. ;-)", _
                  vbYesNo + vbQuestion, "Continue?")
    ' Check if the user clicked "No"
    If response = vbNo Then
        Exit Sub
    End If

    Worksheets("scatter").Activate
'Dim indicators As Variant
'Dim j As Long
'Dim oneDArray() As Variant
'' Convert the range to a 2D array
'indicators = Range("G3:G18").Value
'' Resize the 1D array to hold the values
'ReDim oneDArray(1 To UBound(indicators, 1))
'' Transfer values from 2D array to 1D array
'For j = 1 To UBound(indicators, 1)
'    oneDArray(j) = indicators(j, 1)
'Next j

    'Dim indic As Range
     '   For Each indic In indicators
      '         Debug.Print indic.Value
       ' Next indic

    indicators = Array("ID0", "ID1", "ID4", "ID7", "ID17", "ID20", "ID22", "ID31", "ID50", "ID61", "ID66", "ID83", "ID99", "ID106", "ID109", "ID113", "ID114")
    Application.DisplayAlerts = False
    DataSourceName = "SCATTER"
    Set originalWB = ActiveWorkbook
    Worksheets("scatter").Activate
    actSh = ActiveSheet.Name

    Workbooks.Add.SaveAs Filename:=ThisWorkbook.Path & "\static_scoreboard.xlsx"
    Workbooks.Open Filename:=ThisWorkbook.Path & "\static_scoreboard.xlsx"
    Set finalWB = ActiveWorkbook

    For i = LBound(indicators) To UBound(indicators)
    'For i = 4 To 6
        originalWB.Activate
        Sheets(actSh).Select
        ActiveWorkbook.SlicerCaches("Slicer_ind").VisibleSlicerItemsList = Array( _
            "[" & DataSourceName & "].[ind].&[" & indicators(i) & "]")
        Application.CalculateUntilAsyncQueriesDone

        'Duplicate Sheet
        ActiveSheet.Copy After:=originalWB.Sheets(Sheets.Count)
        Cells.Select
        Selection.Copy
        Range("A1").Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False


        'Delete non-static area
        Dim rng1 As Range
        Set rng1 = ActiveSheet.UsedRange.Find("OUTPUT", , xlValues, xlWhole)
        If Not rng1 Is Nothing Then
            'MsgBox ("Found in column " & rng1.Column)
            Range(Columns(1), Columns(rng1.Column)).Select
            Application.CutCopyMode = False
            Selection.Delete Shift:=xlToLeft
        Else
            MsgBox ("Not found")
        End If

        'Move to static workbook
        ActiveSheet.Move After:=finalWB.Sheets(finalWB.Sheets.Count)
        'Delete old chart
        Dim sh As Worksheet
        For Each sh In Worksheets
            If sh.Name Like indicators(i) Then Sheets(sh.Name).Delete: Exit For
        Next
        ActiveSheet.Name = indicators(i)


     Next

    finalWB.Save
    'finalWB.Close

    MsgBox "extract_scatter_chart macro finished. Now run 'Format Dissemination 3' macro"

    Workbooks("Pivot_for_Scatters.xlsm").Close SaveChanges:=True

End Sub

