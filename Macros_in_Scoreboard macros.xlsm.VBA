Sub format_disso1()

Dim WS_Count As Integer
Dim I As Integer, c As Integer
Dim bookmarks As Range

    Windows("output.xlsx").Activate
    WS_Count = ActiveWorkbook.Worksheets.Count - 1 ' -1 because to avoid touching sheet "Cut_offs II"

    For I = 1 To WS_Count

        Worksheets(I).Select

        ActiveWindow.Zoom = 80

        ActiveSheet.Columns("A:A").Delete
        ActiveSheet.Columns("A:A").ColumnWidth = 15

    Next I

    For I = 1 To WS_Count - 1

        Worksheets(I).Activate

        ActiveSheet.Rows("1:1").Delete
        ActiveSheet.Rows("1:1").RowHeight = 75
        ActiveSheet.Rows("2:2").RowHeight = 30

        If I <> 4 Then
            ActiveSheet.Rows("3:3").Delete
        End If


        'ActiveSheet.Range("B3:DD800").NumberFormat = "0.0"

        ActiveSheet.Range("B3:DD800").Select

        With Selection
            .NumberFormat = "0.0"
            .Value = .Value
        End With


        If I = 3 Then
            ActiveSheet.Range("B3:DD800").Select

            With Selection
                .HorizontalAlignment = xlRight
                .Replace "nan", ""
            End With
        End If

        If I = 5 Then
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

    Next I

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

    For I = 1 To 16

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

    Next I

    Rows("2:2").RowHeight = 22.2

    Workbooks("bookmarks.csv").Close

    Windows("output.xlsx").Activate
    Worksheets("Cut_offs II").Range("C2:F32").NumberFormat = "0.0"
    Worksheets("Cut_offs II").Columns(1).AutoFit
    Worksheets("Cut_offs II").Columns(2).AutoFit


End Sub
Sub format_disso2()

Dim WS_Count As Integer
Dim I As Integer
Dim ids As Range, cell As Range, indicators As Range

    Workbooks.Open Filename:= _
        "U:\04 Data and tools\Reports\scoreboard\Headline indicators table.csv"
    Set indicators = Range("A1:B16")

    Windows("COLOURS.xlsx").Activate
    WS_Count = ActiveWorkbook.Worksheets.Count

    Worksheets(1).Select

    ActiveWindow.Zoom = 80
    ActiveSheet.Columns("A:A").Delete
    ActiveSheet.Columns("A:A").ColumnWidth = 25
    ActiveSheet.Columns("B:Q").ColumnWidth = 15

    Range("B1:Q1").Select
    With Selection
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlCenter
        .WrapText = True
        .Font.Bold = True
    End With

    Rows("1:1").RowHeight = 102
    Rows("2:8").EntireRow.AutoFit

    Set ids = Range("B1:Q1")

    For Each cell In ids

        cell.Value = Application.VLookup(cell.Value, indicators, 2, False)

    Next cell

    Application.DisplayAlerts = False
    For I = WS_Count To 2 Step -1
        Worksheets(I).Delete
    Next I
    Application.DisplayAlerts = True

    Windows("Headline indicators table.csv").Close

End Sub
Sub format_disso3()

Dim WS_Count As Integer
Dim I As Integer
Dim sh_name As String
Dim freq As String
Dim rng As Range
Dim cell As Range

    'freq = InputBox("Are these quarterly or yearly indicators? Type q for quarterly or y for yearly")

    Windows("static_scoreboard.xlsx").Activate
    'Windows("static_scoreboard_q.xlsx").Activate
    Dim ws As Worksheet
    ' Loop through each worksheet in reverse order
    ' Reverse order is used to avoid skipping sheets when deleting
    For I = Sheets.Count To 1 Step -1
        Set ws = Sheets(I)
        ' Check if the name of the worksheet starts with "Sheet"
        If ws.Name Like "Sheet*" Then
            Application.DisplayAlerts = False ' Disable alerts to avoid confirmation dialog
            ws.Delete
            Application.DisplayAlerts = True  ' Enable alerts again
        End If
    Next I


    WS_Count = ActiveWorkbook.Worksheets.Count


    For I = 1 To WS_Count

        Worksheets(I).Activate
        Columns("A:H").Select
        Selection.Insert Shift:=xlToRight, CopyOrigin:=xlFormatFromLeftOrAbove

    Next I

    Workbooks.Open Filename:= _
        "U:\04 Data and tools\Reports\scoreboard\Colour template.xlsx"

    Range("A1:G14").Select
    Selection.Copy

    Windows("static_scoreboard.xlsx").Activate
    'Windows("static_scoreboard_q.xlsx").Activate

    For I = 1 To WS_Count

        Worksheets(I).Activate
        Range("A1").Select
        ActiveSheet.Paste

    Next I

    Application.CutCopyMode = False

    For I = 2 To WS_Count + 1

        Windows("COLOURS.xlsx").Activate
        Worksheets(I).Activate
        sh_name = ActiveSheet.Name
        Range("C3:G7").Copy
        Windows("static_scoreboard.xlsx").Activate
        'Windows("static_scoreboard_q.xlsx").Activate
        Sheets(sh_name).Select
        Range("C10").Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
            :=False, Transpose:=False

    Next I

    Application.CutCopyMode = False

    For I = 1 To WS_Count

        Worksheets(I).Activate
        Columns("B:G").ColumnWidth = 24
        Set rng = ActiveSheet.Range("C10:G14")
        For Each cell In rng
            cell.EntireRow.AutoFit
        Next cell

    Next I

    Workbooks("Colour template.xlsx").Close

End Sub


Sub format_disso4()

Dim data As Range
Dim col_count As Integer
Dim I As Integer
Dim WS_Count As Integer
Dim MS As String
Dim r As Integer
Dim currentDate As String

    currentDate = Format(Date, "dd mmmm yyyy")

    Windows("SCATTER.csv").Activate

    col_count = Range("A1", ActiveSheet.Range("a1").End(xlDown)).Count

    Columns("B:B").Select
        Selection.Insert Shift:=xlToRight, CopyOrigin:=xlFormatFromLeftOrAbove

    Range("B1").Value = "ind_num"

    For I = 1 + 1 To col_count

        Cells(I, 2).Value = Mid(Cells(I, 1), 3, 3)

    Next I

    Range("A1").CurrentRegion.Name = "data"

    Range("data").Sort Key1:=Range("D1"), Order1:=xlAscending, Header:=xlYes, Key2:=Range("B1"), Order2:=xlAscending

    Windows("Template.xlsx").Activate
    WS_Count = ActiveWorkbook.Worksheets.Count

    For I = 1 To WS_Count

        Worksheets(I).Select
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

    Next I

    Windows("SCATTER.csv").Activate
    DeleteColumnByTitle ("ind_num") ' clean-up
    Windows("Template.xlsx").Activate

End Sub

' Option Explicit

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

Sub testing()
        ' Placeholder macro for testing new code snippets
        Range("I1:I17").Borders(xlEdgeRight).LineStyle = xlContinuous
        Range("I1:I17").Borders(xlEdgeRight).Weight = xlThin
End Sub
