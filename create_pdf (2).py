# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4, inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import Image
import qrcode
from PIL import Image as PilImage
from io import BytesIO  # Fayl saqlash o'rniga xotirada ishlatish uchun
from reportlab.pdfgen import canvas
import sys


if not os.access(".", os.W_OK):
    print("Yozish ruxsati yo'q")



def add_page_number(canvas, doc, date_time=None, line_color=colors.black, font_size=8):
    page_number = canvas.getPageNumber()  # Get the current page number
    
    # Set the custom font and size, dynamically adjust font size with the given argument
    canvas.setFont('DejaCondedBoldItalic', (font_size * 0.0138889) * inch)  
    
    # Draw page number at the specified position
    canvas.drawString(201 * mm, 0.39 * inch, f"{page_number}")
    
    # If date_time is provided, draw it at the top-right position
    if date_time:
        canvas.drawString(6.8 * inch, 11.25 * inch, date_time)
    
    # Set the stroke color dynamically using the provided argument
    canvas.setStrokeColor(line_color)
    canvas.setLineWidth(0.5)  # Set the line width
    
    # Draw lines at the bottom and top of the page
    canvas.line(0.7 * inch, 0.5 * inch, 202.78 * mm, 0.5 * inch)
    canvas.line(0.7 * inch, 11.2 * inch, 202.78 * mm, 11.2 * inch)

# Register custom fonts
def register_custom_fonts():
    font_dir = "fonts"  # Directory where font files are located
    fonts = {
        "CustomFont": "DejaVuSerif.ttf",
        "CustomFontBold": "DejaVuSans-Bold.ttf",
        "CustomFontReg": "DejaVuSerifCondensed.ttf",
        "CustomFontBold": "DejaVuSerifCondensed-Bold.ttf",
        "CustomSans": "DejaVuSansCondensed-Bold.ttf",
        "CustomSansReg": "DejaVuSansCondensed.ttf",
        "DejaCondedBoldItalic": "DejaVuSerifCondensed-BoldItalic.ttf",
    }
    for font_name, font_file in fonts.items():
        font_path = os.path.join(font_dir, font_file)
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(font_name, font_path))
        else:
            raise FileNotFoundError(f"Font file not found: {font_path}")


# Create the final PDF
def create_final_pdf():
    register_custom_fonts()  # Register fonts
    buffer = BytesIO()

    # Generate PDF filename with current timestamp
    current_time = datetime.now().strftime("%H-%M-%S")
    output_path = f"output_with_custom_font_{current_time}.pdf"

    # Initialize the PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=15,
        leftMargin=0.6 * inch,
        topMargin=50,
        bottomMargin=50,
    )
    elements = []

    # Define styles
    styles = getSampleStyleSheet()

    custom_heading = ParagraphStyle(
        name="CustomHeading",
        parent=styles["Title"],
        fontName="CustomFont",
        fontSize=14,
        leading=16,
        alignment=1,  # Center alignment
        textColor=colors.HexColor("#ffff"),
    )

    custom_normal = ParagraphStyle(
        name="CustomNormal",
        parent=styles["Normal"],
        fontName="CustomFontReg",
        fontSize=9,
        leading=12,
        wordWrap="CJK",  # Enables word wrapping
        alignment=TA_CENTER,  # Matnni markazga hizalash
    )
    custom_normal_footer= ParagraphStyle(
        name="CustomNormal",
        parent=styles["Normal"],
        fontName="CustomFontReg",
        fontSize=9,
        leading=12,
        wordWrap="CJK",  # Enables word wrapping
        alignment=TA_LEFT,  # Matnni markazga hizalash
    )

    custom_normal_bold = ParagraphStyle(
        name="CustomNormal",
        parent=styles["Normal"],
        fontName="CustomFontReg",
        fontSize=(22.5 / 72) * inch,
        leading=12,
        wordWrap="CJK",  # Enables word wrapping
        alignment=TA_RIGHT,  # Matnni markazga hizalash
    )
    custom_normal_right = ParagraphStyle(
        name="CustomNormal",
        parent=styles["Normal"],
        fontName="CustomFontReg",
        fontSize=9,
        leading=12,
        leftIndent=-8,  # 0 px left indent
        wordWrap="CJK",  # Enables word wrapping
        alignment=TA_RIGHT,  # Matnni markazga hizalash
        textColor=colors.HexColor("#333333"),
    )

    custom_normal_left = ParagraphStyle(
        name="CustomNormal",
        parent=styles["Normal"],
        fontName="CustomFontReg",
        fontSize=9,
        leading=12,
        leftIndent=-8,  # 0 px left indent
        wordWrap="CJK",  # Enables word wrapping
        alignment=TA_LEFT,  # Matnni markazga hizalash
        textColor=colors.HexColor("#333333"),
    )

    custom_center_style = ParagraphStyle(
        name="CustomCenter",
        parent=styles["Normal"],
        fontName="CustomFont",
        fontSize=14,
        leading=14,
        leftIndent=49,  # Qo'shimcha sozlamalar
        rightIndent=49,  # Qo'shimcha sozlamalar
        alignment=TA_CENTER,  # Markazlashtirish
        textColor=colors.HexColor("#000"),
    )

    deja_serif = ParagraphStyle(
        name="DejaSerif",
        parent=styles["Normal"],
        fontName="CustomFontReg",
        fontSize=14,
        leading=16,
        leftIndent=40,  # Qo'shimcha sozlamalar
        rightIndent=40,  # Qo'shimcha sozlamalar
        alignment=TA_CENTER,  # Markazlashtirish
        textColor=colors.HexColor("#0078bb"),
    )
    deja_serif_bold = ParagraphStyle(
        name="DejaSerifBold",
        parent=styles["Normal"],
        fontName="CustomFontBold",
        fontSize=10,
        leading=14,
        leftIndent=20,  # Qo'shimcha sozlamalar
        rightIndent=20,  # Qo'shimcha sozlamalar
        alignment=TA_CENTER,  # Markazlashtirish
        textColor=colors.HexColor("#0078bb"),
    )

    deja_sans = ParagraphStyle(
        name="CustomSans",
        parent=styles["Normal"],
        fontName="CustomSans",
        fontSize=14,
        leading=14,
        leftIndent=20,  # Qo'shimcha sozlamalar
        rightIndent=20,  # Qo'shimcha sozlamalar
        alignment=TA_CENTER,  # Markazlashtirish
        textColor=colors.HexColor("#000"),
    )
    deja_sans_left = ParagraphStyle(
        name="CustomSansReg",
        parent=styles["Normal"],
        fontName="CustomSansReg",  # Agar bu font sizda bo'lmasa, o'zgartiring
        fontSize=10,
        leading=14,
        spaceBefore=0,  # 0 px space before
        spaceAfter=0,  # 0 px space after
        # 0 px left indent
        rightIndent=0,  # 0 px right indent
        firstLineIndent=0,  # 0 px first line indent
        alignment=TA_LEFT,  # Chapga hizalanish
        textColor=colors.HexColor("#333333"),  # Matn rangi
    )
    # Add headings and spacing
    para1 = Paragraph("Single Portal of Interactive Public Services", deja_serif_bold)

    # 2. Image (Rasm)
    image_path = "../python-app/image/logo.png"  # Rasm faylini to'g'ri yo'lga o'zgartiring
    print(os.getcwd())
    if os.path.exists(image_path):
        logo = Image(image_path)
        logo.drawWidth = 25.2 * mm
        logo.drawHeight = 25.2 * mm
    else:
        logo = Paragraph("Rasm topilmadi", custom_normal)
        print(f"Rasm fayli topilmadi: {image_path}")

    gov_image = "../python-app/image/gov_logo.png"
    if os.path.exists(gov_image):
        gov_logo = Image(gov_image)
        gov_logo.drawHeight = 9 * mm
        gov_logo.drawWidth = 39.5 * mm
    else:
        gov_logo = Paragraph("Rasm topilmadi", custom_normal)
        print(f"Rasm fayli topilmadi: {gov_image}")
    # 3. Ikkinchi Paragraph
    para2 = [
        Paragraph("The State", custom_center_style),
        Paragraph("Tax Committee ", custom_center_style),
        Paragraph("of the", custom_center_style),
        Paragraph("Uzbekistan", custom_center_style),
    ]

    # Jadval ma'lumotlari (Uchta Elementni Yonma-Yon Qo'yish)
    table_data = [[[gov_logo, para1], logo, para2]]
    PAGE_WIDTH, PAGE_HEIGHT = A4

    available_width = PAGE_WIDTH
    print(available_width)
    print(PAGE_HEIGHT)
    # Ustunlar uchun foizlar (umumiy 100%)
    col_percentages = [30, 20, 35]  # Foizlarni kerakli miqdorga moslang

    # Har bir ustunning kengligini hisoblash
    col_widths = [available_width * (percent / 100) for percent in col_percentages]

    # Jadvalni yaratish
    table = Table(table_data, colWidths=col_widths, hAlign="LEFT")

    # Jadval uslublari
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # Vertikal markazlashtirish
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Gorizontal markazlashtirish
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),  # Pastki padding
                # Agar kerak bo'lsa, chegara chizig'ini qo'shishingiz mumkin
                # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, (0.5 * inch)))

    # Add document details
    detail1 = [
        "No 7731-5467-0292-04f3-9ef9-6216-1743",
        "Document creation date: 2024-10-06",
        "Application number: 153017206",
    ]
    detail2 = [
        "Document issued: MAXMASOLIYEV OTAJON ISOMIDDIN O'G'LI",
        "PINFL: 53112016120015",
    ]

    formatted_detail1 = [Paragraph(detail1[0], custom_normal_left)]
    formatted_detail2 = [Paragraph(detail2[0], custom_normal_right)]

    # detail1 va detail2 ni formatlash
    for i in range(1, len(detail1)):
        formatted_detail1.append(Paragraph(detail1[i], custom_normal_left))

    for i in range(1, len(detail2)):
        formatted_detail2.append(Paragraph(detail2[i], custom_normal_right))

    # Har bir ustun uchun kengliklarni hisoblash
    left_column_width = (available_width - 81) * 0.5  # Chap ustun uchun 50%
    right_column_width = (available_width - 81) * 0.5  # O'ng ustun uchun 50%

    # Yangi jadvalni yaratish
    table2 = Table(
        [[formatted_detail1, formatted_detail2]],
        colWidths=[left_column_width, right_column_width],
    )

    # Jadval uslublari
    table2.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # Vertikal markazlashtirish
                (
                    "ALIGN",
                    (0, 0),
                    (0, -1),
                    "LEFT",
                ),  # Chap ustun uchun matnni chapga hizalash
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT",
                ),  # O'ng ustun uchun matnni o'ngga hizalash
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),  # Pastki padding
                # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Chegaralarni qo'shish
            ]
        )
    )

    # Jadvalni PDF ga qo'shish
    elements.append(table2)
    elements.append(Spacer(1, (0.5 * inch)))
    elements.append(Paragraph("INCOME STATEMENT", deja_sans))
    elements.append(Spacer(1, (0.5 * inch)))
    elements.append(
        Paragraph("Name: MAXMASOLIYEV OTAJON ISOMIDDIN O'G'LI", deja_sans_left)
    )

    doc.build(
        elements,
        onFirstPage=lambda canvas, doc: add_page_number(canvas, doc, date_time="2024-10-08 14:22:00", line_color=colors.black, font_size=8),
        onLaterPages=lambda canvas, doc: add_page_number(canvas, doc, date_time="2024-10-08 14:22:00", line_color=colors.black, font_size=8)
    )
    buffer.seek(0) 
    print(buffer)
    print(f"Final PDF with custom font created successfully: {output_path}")
    return buffer



if __name__ == "__main__":
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]  # Node.js dan kiritilgan argumentni olish
        print(output_filename)
        create_final_pdf()

        
    else:
        print("Iltimos, chiqish fayli nomini kiritng, masalan: `output.pdf`")
