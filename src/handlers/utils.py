import io

import requests
from aiogram.types.input_file import BufferedInputFile
from docx import Document
# from docx2pdf import convert
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from src.handlers.schemas import OrderResponse


def create_facture(data: OrderResponse) -> BufferedInputFile:
    """
        hisob faktura yaratadi
    """
    # Создание документа
    doc = Document()

    # Настройка шрифта по умолчанию
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(14)
    para_format = style.paragraph_format
    #
    doc.sections[0].bottom_margin = Inches(0.4)
    doc.sections[0].left_margin = Inches(0.4)
    doc.sections[0].top_margin = Inches(0.4)
    doc.sections[0].right_margin = Inches(0.4)
    # header qismini qo'shsih
    header = doc.add_paragraph()
    header.add_run("___.05.2024 sanadagi _____-sonli shartnomaga")
    header.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    header.paragraph_format.space_after = Pt(0)
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER

    header2 = doc.add_paragraph()
    header2.add_run("___.05.2024 sanadagi ___-sonli")
    header2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header2.paragraph_format.space_after = Pt(0)
    header2.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    # header.paragraph_format.line_spacing = Pt(1.0)

    # ===================================
    empty_pg = doc.add_paragraph()
    run = empty_pg.add_run("")
    run.font.size = Pt(20)
    empty_pg.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    empty_pg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # ==============================================
    header = doc.add_paragraph()
    run = header.add_run("YUK XATI")
    run.font.size = Pt(26)
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # -------------------------------------

    # Добавление информации о поставщике и получателе

    yuridik_data = [
        [
            {"Yetkazib beruvchi:": data.company.name},
            {"Qabul qiluvchi:": data.dmtt.name},
        ],
        [
            {"Manzil:": data.company.address},
            {"Manzil:": data.dmtt.address},
        ],
        [{"Tel:": data.company.phone_number},
         {"Tel:": data.dmtt.user.phone_number}],
        [{"STIR:": data.company.stir}, {"STIR:": data.dmtt.stir}],
    ]

    table = doc.add_table(rows=4, cols=2)

    for i in range(4):
        for j in range(2):
            cell = table.cell(i, j)
            p = cell.paragraphs[0]
            item = yuridik_data[i][j]
            key, value = item.popitem()
            run = p.add_run(key)
            run.bold = True
            p.add_run(value)

            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    # ------------------------------------------------------------
    for _ in range(2):
        p = doc.add_paragraph()
        run = p.add_run()
        run.font.size = Pt(12)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        p.paragraph_format.space_after = Pt(0)
    # ----------------------
    # Добавление таблицы с товарами
    products_table = doc.add_table(rows=1, cols=7)
    products_table.style = "Table Grid"
    headers = [
        "T/r",
        "Mahsulot nomi",
        "O'lchov birligi",
        "Miqdori",
        "Narxi (so'm)",
        "QQS",
        "Yetkazib berish qiymati",
    ]
    for i, header in enumerate(headers):
        cell = products_table.cell(0, i)
        cell.text = header
        cell.paragraphs[0].runs[0].font.bold = True  # Sarlavhani qalin qilish
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    products_table.columns[0].width = Inches(0.42)
    products_table.columns[1].width = Inches(2.11)
    products_table.columns[2].width = Inches(0.89)
    products_table.columns[3].width = Inches(0.89)
    products_table.columns[4].width = Inches(1.08)
    products_table.columns[5].width = Inches(0.9)
    products_table.columns[6].width = Inches(1.36)

    # Заполнение таблицы данными
    i = 0
    for item in data.items:
        i += 1
        row_cells = products_table.add_row().cells
        row_cells[0].text = str(i)
        row_cells[1].text = item.product_name  # Примерное название
        row_cells[2].text = "kg"
        row_cells[3].text = str(item.count)  # Примерное количество
        row_cells[4].text = "50000"
        row_cells[5].text = "QQS siz"
        row_cells[6].text = "100000"

        row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        row_cells[5].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[6].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        for cell in row_cells:
            cell.paragraphs[0].paragraph_format.space_after = Pt(3)
            cell.paragraphs[0].paragraph_format.space_before = Pt(3)

        # ------------------------

    doc.add_paragraph()

    # summary
    header = doc.add_paragraph()
    run = header.add_run(
        "Jami yetkazib berilgan mahsulotlarning umumiy qiymati - ________________ so'm"
    )
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # footer table
    table = doc.add_table(rows=2, cols=2)

    table.cell(0, 0).text = "Yetkazib beruvchi:"
    table.cell(0, 1).text = "Qabul qiluvchi:"
    table.cell(1, 0).text = data.company.name
    table.cell(1, 1).text = "______________________         ______"

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    dd = BufferedInputFile(file_stream.read(), filename="test.docx")
    return dd
