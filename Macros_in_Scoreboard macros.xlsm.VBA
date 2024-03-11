Sub format_disso1()

Dim WS_Count As Integer
Dim i As Integer, c As Integer
Dim bookmarks As Range
Dim filepath As String

    filepath = Workbooks("Scoreboard macros.xlsm").Sheets(1).Range("B20").Value
    filepath = Replace(filepath, "dissemination", "output")
    MsgBox "Opening: " & filepath & "output.xlsx", vbInformation, "Info"
    Workbooks.Open Filename:=filepath & "output.xlsx"



    Windows("output.xlsx").Activate
    WS_Count = ActiveWorkbook.Worksheets.Count - 1 ' -1 because to avoid touching sheet "Cut_offs II"

    For i = 1 To WS_Count

        Worksheets(i).Select

        ActiveWindow.Zoom = 80

        ActiveSheet.Columns("A:A").Delete
        ActiveSheet.Columns("A:A").ColumnWidth = 15

    Next i

    For i = 1 To WS_Count - 1

        Worksheets(i).Activate

        ActiveSheet.Rows("1:1").Delete
        ActiveSheet.Rows("1:1").RowHeight = 75
        ActiveSheet.Rows("2:2").RowHeight = 30

        If i <> 4 Then
            ActiveSheet.Rows("3:3").Delete
        End If


        'ActiveSheet.Range("B3:DD800").NumberFormat = "0.0"

        ActiveSheet.Range("B3:DD800").Select

        With Selection
            .NumberFormat = "0.0"
            .Value = .Value
        End With


        If i = 3 Then
            ActiveSheet.Range("B3:DD800").Select

            With Selection
                .HorizontalAlignment = xlRight
                .Replace "nan", ""
            End With
        End If

        If i = 5 Then
           ActiveSheet.Range("B3:DD800").NumberFormat = "0.00"
        End If

        Columns("A:AW").ColumnWidth = 9.71

        Rows("1:2").Select
        With Selection
            .VerticalAlignment = xlCenter
            .WrapText = True
            .Orientation = 0
            .AddIndent = False
            .IndentLevel = 0
            .ShrinkToFit = False
            .ReadingOrder = xlContext
        End With

    Next i

    Sheets("Differences").Activate
    Columns("A:A").Select
    Selection.Delete Shift:=xlToLeft
    Rows("3:3").RowHeight = 26.25
    Rows("4:4").Delete
    Range("A1") = "Indicator"
    Range("A2") = "year"
    Range("A3") = "diff"

'adding bookmarks

    Workbooks.Open Filename:= _
        "U:\04 Data and tools\Reports\scoreboard\bookmarks.csv"
    Set bookmarks = Range("D1:E122")

    Windows("output.xlsx").Activate
    Sheets("Headline").Activate
    Rows("2:2").Select
    Selection.Insert Shift:=xlDown, CopyOrigin:=xlFormatFromLeftOrAbove
    Range("A2") = "bookmarks"

    c = 2

    For i = 1 To 16

        Cells(2, c).Select

        If c = 5 Then
            ActiveCell.Resize(1, 1).Select
        Else: ActiveCell.Resize(1, 3).Select

        End If

        With Selection
            .HorizontalAlignment = xlCenter
            .VerticalAlignment = xlCenter
            .WrapText = False
            .Orientation = 0
            .AddIndent = False
            .IndentLevel = 0
            .ShrinkToFit = False
            .ReadingOrder = xlContext
            .MergeCells = False
        End With

        Selection.Merge

        ActiveCell.Value = Application.VLookup(ActiveCell.Offset(-1, 0).Value, bookmarks, 2, False)

        c = c + 3

        If c = 8 Then
            c = c - 2
        End If

    Next i

    Rows("2:2").RowHeight = 22.2

    Workbooks("bookmarks.csv").Close

    Windows("output.xlsx").Activate
    special_adjustments_to_file1 ' <---- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    Worksheets("Cut_offs II").Range("C2:F32").NumberFormat = "0.0"
    Worksheets("Cut_offs II").Columns(1).AutoFit
    Worksheets("Cut_offs II").Columns(2).AutoFit
    filepath = Workbooks("Scoreboard macros.xlsm").Sheets(1).Range("B24").Value
    ' Turn off warnings to overwrite the file without prompts
    Application.DisplayAlerts = False
    ' Save the active workbook to the specified filepath
    ActiveWorkbook.SaveAs Filename:=filepath
    ActiveWorkbook.Close
    ' Turn warnings back on
    Application.DisplayAlerts = True
    MsgBox "Saved transformed output.xlsx as: " & filepath, vbInformation, "Info"

End Sub

Sub special_adjustments_to_file1()
    Worksheets("Headline").Range("B2:H2").UnMerge
    Application.DisplayAlerts = False ' Suppress warnings for merge
        For Each addr In Array("B2:C2", "D2:F2", "G2:H2") ' the ranges to which you want to apply merge and borders
            Worksheets("Headline").Range(addr).Merge
            With Worksheets("Headline").Range(addr).Borders
                .LineStyle = xlContinuous
                .Color = vbBlack
                .Weight = xlThin
            End With
        Next addr
    Application.DisplayAlerts = False ' Unsuppress warnings for merge
    With Worksheets("Headline")
        .Range("B3").Value = 2016
        .Range("B2").Value = "https://circabc.europa.eu/ui/group/d14c857a-601d-438a-b878-4b4cebd0e10f/library/c5a8b987-1e37-44d7-a20e-2c50d6101d27/details"
        .Range("D2").Value = "https://ec.europa.eu/eurostat/databrowser/bookmark/e48bf39d-5176-410d-b32f-f4a5d22fbfdd?lang=en"
        .Range("G2").Value = "https://ec.europa.eu/eurostat/databrowser/bookmark/40ecd88d-1514-4d6b-8260-3c4f5b8f4d0a?lang=en"
    End With
    Worksheets("Flags").Range("B2").Value = 2016
    Worksheets("Headline_flags").Range("B2").Value = 2016

End Sub


Sub format_disso2()

Dim WS_Count As Integer
Dim i As Integer
Dim ids As Range, cell As Range, indicators As Range
Dim filepath As String

    filepath = Workbooks("Scoreboard macros.xlsm").Sheets(1).Range("B20").Value
    filepath = Replace(filepath, "dissemination", "output")
    MsgBox "Opening: " & filepath & "COLOURS.xlsx", vbInformation, "Info"
    Workbooks.Open Filename:=filepath & "COLOURS.xlsx"

    Windows("COLOURS.xlsx").Activate
    Sheets("All").Select
    Range("D2:J18").Select
    With Selection
        .HorizontalAlignment = xlGeneral
        .VerticalAlignment = xlCenter
        .WrapText = True
        .Orientation = 0
        .AddIndent = False
        .IndentLevel = 0
        .ShrinkToFit = False
        .ReadingOrder = xlContext
        .MergeCells = False
    End With
    ' Turn off warnings to overwrite the file without prompts
    Application.DisplayAlerts = False
    ' Save the active workbook to the specified filepath
    filepath = Workbooks("Scoreboard macros.xlsm").Sheets(1).Range("B25").Value
    ActiveWorkbook.SaveAs Filename:=filepath
    ActiveWorkbook.Close
    ' Turn warnings back on
    Application.DisplayAlerts = True
    MsgBox "Saved COLOURS.xlsx as: " & filepath, vbInformation, "Info"

'    Workbooks.Open Filename:= _
'        "U:\04 Data and tools\Reports\scoreboard\Headline indicators table.csv"
'    Set indicators = Range("A1:B16")
'
'    Windows("COLOURS.xlsx").Activate
'    WS_Count = ActiveWorkbook.Worksheets.Count
'
'    Worksheets(1).Select
'
'    ActiveWindow.Zoom = 80
'    ActiveSheet.Columns("A:A").Delete
'    ActiveSheet.Columns("A:A").ColumnWidth = 25
'    ActiveSheet.Columns("B:Q").ColumnWidth = 15
'
'    Range("B1:Q1").Select
'    With Selection
'        .HorizontalAlignment = xlCenter
'        .VerticalAlignment = xlCenter
'        .WrapText = True
'        .Font.Bold = True
'    End With
'
'    Rows("1:1").RowHeight = 102
'    Rows("2:8").EntireRow.AutoFit
'
'    Set ids = Range("B1:Q1")
'
'    For Each cell In ids
'
'        cell.Value = Application.VLookup(cell.Value, indicators, 2, False)
'
'    Next cell
'
'    Application.DisplayAlerts = False
'    For i = WS_Count To 2 Step -1
'        Worksheets(i).Delete
'    Next i
'    Application.DisplayAlerts = True
'
'    Windows("Headline indicators table.csv").Close

End Sub
Sub format_disso3()

Dim WS_Count As Integer
Dim i As Integer
Dim sh_name As String
Dim freq As String
Dim rng As Range
Dim cell As Range
Dim filepath As String

    'freq = InputBox("Are these quarterly or yearly indicators? Type q for quarterly or y for yearly")
    filepath = Workbooks("Scoreboard macros.xlsm").Sheets(1).Range("B20").Value
    filepath = Replace(filepath, "dissemination", "output")
    MsgBox "Opening: " & filepath & "COLOURS.xlsx", vbInformation, "Info"
    Workbooks.Open Filename:=filepath & "COLOURS.xlsx"
    MsgBox "Opening: U:\04 Data and tools\Reports\scoreboard\static_scoreboard.xlsx", vbInformation, "Info"
    Workbooks.Open Filename:="U:\04 Data and tools\Reports\scoreboard\static_scoreboard.xlsx"


    Windows("static_scoreboard.xlsx").Activate
    'Windows("static_scoreboard_q.xlsx").Activate
    Dim ws As Worksheet
    ' Loop through each worksheet in reverse order
    ' Reverse order is used to avoid skipping sheets when deleting
    For i = Sheets.Count To 1 Step -1
        Set ws = Sheets(i)
        ' Check if the name of the worksheet starts with "Sheet"
        If ws.Name Like "Sheet*" Then
            Application.DisplayAlerts = False ' Disable alerts to avoid confirmation dialog
            ws.Delete
            Application.DisplayAlerts = True  ' Enable alerts again
        End If
    Next i


    WS_Count = ActiveWorkbook.Worksheets.Count


    For i = 1 To WS_Count

        Worksheets(i).Activate
        Columns("A:H").Select
        Selection.Insert Shift:=xlToRight, CopyOrigin:=xlFormatFromLeftOrAbove

    Next i

    Workbooks.Open Filename:= _
        "U:\04 Data and tools\Reports\scoreboard\Colour template.xlsx"

    Range("A1:G14").Select
    Selection.Copy

    Windows("static_scoreboard.xlsx").Activate
    'Windows("static_scoreboard_q.xlsx").Activate

    For i = 1 To WS_Count

        Worksheets(i).Activate
        Range("A1").Select
        ActiveSheet.Paste

    Next i

    Application.CutCopyMode = False

    For i = 2 To WS_Count + 1

        Windows("COLOURS.xlsx").Activate
        Worksheets(i).Activate
        sh_name = ActiveSheet.Name
        Range("C3:G7").Copy
        Windows("static_scoreboard.xlsx").Activate
        'Windows("static_scoreboard_q.xlsx").Activate
        Sheets(sh_name).Select
        Range("C10").Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
            :=False, Transpose:=False

    Next i

    Application.CutCopyMode = False

    For i = 1 To WS_Count

        Worksheets(i).Activate
        Columns("B:G").ColumnWidth = 24
        Set rng = ActiveSheet.Range("C10:G14")
        For Each cell In rng
            cell.EntireRow.AutoFit
        Next cell

    Next i

    Workbooks("Colour template.xlsx").Close SaveChanges:=False

    Windows("static_scoreboard.xlsx").Activate
    Sheets("ID22").Select
    ActiveSheet.ChartObjects("Chart 1").Activate
    ActiveChart.Axes(xlCategory).MinimumScale = 60
    ActiveSheet.ChartObjects("Chart 2").Activate
    ActiveChart.Axes(xlCategory).MinimumScale = 60
    Sheets("ID1").Select
    filepath = Workbooks("Scoreboard macros.xlsm").Sheets(1).Range("B26").Value
    ' Turn off warnings to overwrite the file without prompts
    Application.DisplayAlerts = False
    ' Save the active workbook to the specified filepath
    ActiveWorkbook.SaveAs Filename:=filepath
    ActiveWorkbook.Close
    ' Turn warnings back on
    Application.DisplayAlerts = True
    Workbooks("COLOURS.xlsx").Close SaveChanges:=False
    MsgBox "Saved transformed static_scoreboard.xlsx as: " & filepath, vbInformation, "Info"

End Sub


Sub format_disso4()

Dim data As Range
Dim col_count As Integer
Dim i As Integer
Dim WS_Count As Integer
Dim MS As String
Dim r As Integer
Dim currentDate As String
Dim filepath As String

    filepath = Workbooks("Scoreboard macros.xlsm").Sheets(1).Range("B20").Value
    filepath = Replace(filepath, "dissemination", "output")
    MsgBox "Opening: " & filepath & "SCATTER.csv", vbInformation, "Info"
    Workbooks.Open Filename:=filepath & "SCATTER.csv"
    MsgBox "Opening: U:\04 Data and tools\Reports\scoreboard\Template.xlsx", vbInformation, "Info"
    Workbooks.Open Filename:="U:\04 Data and tools\Reports\scoreboard\Template.xlsx"

    currentDate = Format(Date, "dd mmmm yyyy")

    Windows("SCATTER.csv").Activate

    col_count = Range("A1", ActiveSheet.Range("a1").End(xlDown)).Count

    Columns("B:B").Select
        Selection.Insert Shift:=xlToRight, CopyOrigin:=xlFormatFromLeftOrAbove

    Range("B1").Value = "ind_num"

    For i = 1 + 1 To col_count

        Cells(i, 2).Value = Mid(Cells(i, 1), 3, 3)

    Next i

    Range("A1").CurrentRegion.Name = "data"

    Range("data").Sort Key1:=Range("D1"), Order1:=xlAscending, Header:=xlYes, Key2:=Range("B1"), Order2:=xlAscending

    Windows("Template.xlsx").Activate
    WS_Count = ActiveWorkbook.Worksheets.Count

    For i = 1 To WS_Count

        Worksheets(i).Select
        MS = ActiveSheet.Name

        Windows("SCATTER.csv").Activate
        Range("data").Find(MS, MatchCase:=True).Select
        ActiveCell.Offset(0, 9).Select
        r = ActiveCell.Row

        Range("M2:M17").Offset(r - 2, 0).Replace "", "N/A", xlWhole
        Range("M2:M17").Offset(r - 2, 0).Copy Workbooks("Template.xlsx").Worksheets(MS).Range("R2:R17")
        Range("F2:F17").Offset(r - 2, 0).Copy Workbooks("Template.xlsx").Worksheets(MS).Range("I2:I17")

        Windows("Template.xlsx").Activate

        For Each c In Range("C2:C17")

            c.Interior.Color = c.DisplayFormat.Interior.Color
            c.Font.Color = c.DisplayFormat.Font.Color
            c.Interior.Pattern = c.DisplayFormat.Interior.Pattern

        Next c

        For Each c In Range("I2:I17")

            c.Interior.Color = c.DisplayFormat.Interior.Color
            c.Font.Color = c.DisplayFormat.Font.Color
            c.Interior.Pattern = c.DisplayFormat.Interior.Pattern

        Next c

        Range("C2:I17").FormatConditions.Delete
        Range("R2:R17").Delete
        Range("A19").Value = Replace(Range("A19").Value, "DD MMMM YYYY", currentDate)
        Range("I2:I17").Borders(xlInsideHorizontal).LineStyle = xlContinuous
        Range("I2:I17").Borders(xlInsideHorizontal).Weight = xlThin
        Range("I1:I17").Borders(xlEdgeRight).LineStyle = xlContinuous
        Range("I1:I17").Borders(xlEdgeRight).Weight = xlThin

    Next i

    Windows("SCATTER.csv").Activate
    DeleteColumnByTitle ("ind_num") ' clean-up
    Windows("Template.xlsx").Activate
    filepath = Workbooks("Scoreboard macros.xlsm").Sheets(1).Range("B27").Value
    ' Turn off warnings to overwrite the file without prompts
    Application.DisplayAlerts = False
    ' Save the active workbook to the specified filepath
    ActiveWorkbook.SaveAs Filename:=filepath
    ActiveWorkbook.Close
    Workbooks("SCATTER.csv").Close SaveChanges:=False
    ' Turn warnings back on
    Application.DisplayAlerts = True
    MsgBox "Saved transformed Template.xlsx as: " & filepath, vbInformation, "Info"

End Sub

Sub format_disso5()
Dim filepath As String

    filepath = Workbooks("Scoreboard macros.xlsm").Sheets(1).Range("B20").Value
    filepath = Replace(filepath, "dissemination", "output")
    MsgBox "Opening: " & filepath & "For_SCF_tables_Input_Data_worksheet.csv", vbInformation, "Info"
    Workbooks.Open Filename:=filepath & "For_SCF_tables_Input_Data_worksheet.csv"
    MsgBox "Opening: U:\04 Data and tools\Reports\scoreboard\JER SCF Tables.xlsx", vbInformation, "Info"
    Workbooks.Open Filename:="U:\04 Data and tools\Reports\scoreboard\JER SCF Tables.xlsx"

    Windows("For_SCF_tables_Input_Data_worksheet.csv").Activate
    Range("A1").Select
    Range(Selection, Selection.End(xlDown)).Select
    Range(Selection, Selection.End(xlToRight)).Select
    Selection.Copy
    Windows("JER SCF Tables.xlsx").Activate
    Sheets("NEW For_SCF_tables_Input_Data_w").Select
    ActiveSheet.Paste
    filepath = Workbooks("Scoreboard macros.xlsm").Sheets(1).Range("B28").Value
    ' Turn off warnings to overwrite the file without prompts
    Application.DisplayAlerts = False
    ' Save the active workbook to the specified filepath
    ActiveWorkbook.SaveAs Filename:=filepath
    ActiveWorkbook.Close
    ' Turn warnings back on
    Application.DisplayAlerts = True
    Workbooks("For_SCF_tables_Input_Data_worksheet.csv").Close SaveChanges:=False
    MsgBox "Saved updated `JER SCF Tables.xlsx` as: " & filepath, vbInformation, "Info"

End Sub

Sub fillpattern()
'
' fillpattern Macro
'

'
    ActiveWindow.ActivateNext
    Range("C10:H10").Select
    With Selection.Interior
        .Pattern = xlLightUp
        .PatternColorIndex = xlAutomatic
        .Color = 14277081
        .TintAndShade = 0
        .PatternTintAndShade = 0
    End With
End Sub
Sub Macro2()
'
' Macro2 Macro
'

'
    Range("E11").Select
    ActiveWindow.ActivateNext
    Range("C10:H10").Select
    With Selection.Interior
        .Pattern = xlLightDown
        .PatternColorIndex = xlAutomatic
        .Color = 14277081
        .TintAndShade = 0
        .PatternTintAndShade = 0
    End With
End Sub


Sub DeleteColumnByTitle(colTitle As String)
    Dim ws As Worksheet
    Dim col As Range
    Dim lastCol As Long

    ' Set the active worksheet to a variable
    Set ws = ActiveSheet

    ' Find the last used column in the first row
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column

    ' Loop through each cell in the first row to find the column with the given title
    For Each col In ws.Range(ws.Cells(1, 1), ws.Cells(1, lastCol))
        If col.Value = colTitle Then
            col.EntireColumn.Delete
            Exit For
        End If
    Next col
End Sub

Sub SaveCellsToTextFile()
    Dim fso As Object
    Dim txtFile As Object
    Dim cellContent As String
    Dim filepath As String
    Dim i As Integer

    ' Create a File System Object
    Set fso = CreateObject("Scripting.FileSystemObject")

    ' Define the path of the text file
    filepath = Environ("USERPROFILE") & "\File names to be used.txt"

    ' Create a text file (if it doesn't exist, it will be created; if it exists, it will be overwritten)
    Set txtFile = fso.CreateTextFile(filepath, True)

    ' Loop through cells A1 to A4 to read their content and write to the text file
    For i = 24 To 27
        cellContent = Worksheets("Sheet1").Range("B" & i).Value
        txtFile.WriteLine (cellContent)
    Next i

    ' Close the text file
    txtFile.Close

    ' Open the text file in Notepad
    Shell "notepad.exe " & filepath, vbNormalFocus
End Sub


Sub testing()
        ' Placeholder macro for testing new code snippets
        Range("I1:I17").Borders(xlEdgeRight).LineStyle = xlContinuous
        Range("I1:I17").Borders(xlEdgeRight).Weight = xlThin
End Sub
