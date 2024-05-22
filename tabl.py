import xlsxwriter
from spire.xls import *
from spire.xls.common import *
import jpype
import asposecells

jpype.startJVM()
import asposecells.api
from db import *
def kanban_tabl():
    rows = ['ааааааааааааааааа', 'иииииииииииии', 'сссссссссссссссс']
    data = [('Сделано', rows[0]), ('Делается', rows[1]), ('Надо сделать', rows[2])]
    workbook = xlsxwriter.Workbook('Шаблон Канбан.xlsx')
    worksheet = workbook.add_worksheet()
    for row, (item, price) in enumerate(data):
        worksheet.write(row, 0, item)
        worksheet.write(row, 1, price)
    workbook.close()

    """
    imgOptions = asposecells.api.ImageOrPrintOptions
    imgOptions.setSaveFormat(asposecells.api.SaveFormat.SVG)
    sheet = asposecells.api.workbook.getWorksheets().get(0)

    # create sheet render object
    sr = asposecells.api.SheetRender(sheet, imgOptions)

    # convert sheet to PNG image
    for j in range(0, sr.getPageCount()):
        sr.toImage(j, "WorksheetToImage-out%s" % (j) + ".png")
    """


kanban_tabl()

