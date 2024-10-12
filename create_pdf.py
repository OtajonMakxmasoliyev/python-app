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
import json

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


def format_number_with_spaces(number):
    return f"{number:,}".replace(",", " ")


def convert_timestamp(ms_timestamp):
    """
    Millisekund formatidagi Unix timestampni "YYYY-MM-DD" shaklida sana formatiga aylantiradi.
    
    Args:
        ms_timestamp (int or str): Millisekunddagi Unix timestamp.
    
    Returns:
        str: "YYYY-MM-DD" formatidagi sana.
    """
    # Agar timestamp string bo'lsa, uni integerga aylantirish
    if isinstance(ms_timestamp, int):
        ms_timestamp = ms_timestamp
    else:
        return ms_timestamp
    # Millisekundni sekundga aylantirish
    sec_timestamp = ms_timestamp / 1000
    
    # Datetime obyektini yaratish
    dt = datetime.datetime.fromtimestamp(sec_timestamp)
    
    # Sana formatiga o'zgartirish
    date_str = dt.strftime('%Y-%m-%d')
    
    return date_str


# Create the final PDF
def create_final_pdf(data):
    # print(type(data))
    if not data:
        raise ValueError("Bo'sh data argumenti")
    try:
        objStr = json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ma'lumotni JSON formatida yuklashda xato: {e}")
    
    obj = json.loads(objStr["body"])
    print(objStr)
    register_custom_fonts()  # Register fonts
    buffer = BytesIO()

    # Generate PDF filename with current timestamp
    current_time = datetime.now().strftime("%H-%M-%S")
    # output_path = f"output_with_custom_font_{current_time}.pdf"

    # Initialize the PDF document
    doc = SimpleDocTemplate(
        buffer,
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
    custom_normal_footer = ParagraphStyle(
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
    image_path = "./image/logo.png"  # Rasm faylini to'g'ri yo'lga o'zgartiring
    # print(os.getcwd())
    if os.path.exists(image_path):
        logo = Image(image_path)
        logo.drawWidth = 25.2 * mm
        logo.drawHeight = 25.2 * mm
    else:
        logo = Paragraph("Rasm topilmadi", custom_normal)
     #   print(f"Rasm fayli topilmadi: {image_path}")

    gov_image = "./image/gov_logo.png"
    if os.path.exists(gov_image):
        gov_logo = Image(gov_image)
        gov_logo.drawHeight = 9 * mm
        gov_logo.drawWidth = 39.5 * mm
    else:
        gov_logo = Paragraph("Rasm topilmadi", custom_normal)
      #  print(f"Rasm fayli topilmadi: {gov_image}")
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
#    print(available_width)
#   print(PAGE_HEIGHT)
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
        f"No {obj['id']}",
        f"Document creation date: {convert_timestamp(obj['createdAt'])}",
        f"Application number: {obj['applicationNumber']}",
    ]
    detail2 = [
        f"Document issued: {obj['fullName'].upper()}",
        f"PINFL: {obj['pnfl']}",
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
                ("VALIGN", (0, 0), (-1, -1), "TOP"),  # Vertikal markazlashtirish
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
        Paragraph(f"Name: {obj['fullName'].upper()}", deja_sans_left)
    )
    elements.append(Paragraph("TIN:", deja_sans_left))
    elements.append(Paragraph(f"PRSA: {obj['pnfl']}", deja_sans_left))
    elements.append(Spacer(2, 12))
    elements.append(
        Paragraph(
            "Issued in that the above person has received the following income:",
            deja_sans_left,
        )
    )

    total_salary = 0
    total_tax = 0
    for salary_entry in obj["salaries"]:
        salary = salary_entry['salary']
        tax = salary_entry['tax']
        if salary:
            # MongoDB Extended JSON formatini tekshirish
                salary = int(salary)
        else:
             salary = 0
        total_salary += salary

        if tax:
            # MongoDB Extended JSON formatini tekshirish
                tax = int(tax)
        else:
             tax = 0
        total_tax += tax

    elements.append(Paragraph(f"Total estimated salary: {format_number_with_spaces(total_salary)}", deja_sans_left))
    elements.append(Spacer(0.5, 12))
    elements.append(Paragraph(f"Income tax: {format_number_with_spaces(total_tax)}", deja_sans_left))
    elements.append(Spacer(1.5, 12))

    # Define table data with Paragraphs for better text handling
    table_data = [
        [
            Paragraph(
                "<b>Year</b>",
                custom_normal,
            ),
            Paragraph("<b>Month</b>", custom_normal),
            Paragraph("<b>Enterprise (Organization)</b>", custom_normal),
            Paragraph("<b>Accrued Wage (UZS)</b>", custom_normal),
            Paragraph("<b>Personal Income Tax (PIT)</b>", custom_normal),
            Paragraph("<b>INPS</b>", custom_normal),
        ],
    ]

    # Wrap text in the "Enterprise (Organization)" column
    for salary_entry in obj["salaries"]:
        year = salary_entry["year"]
        month = salary_entry["month"]
        company = salary_entry["company"]
        salary = salary_entry["salary"] 
        tax = salary_entry["tax"]
        bonus = salary_entry["bonus"]
    
        # Formatlash
        formatted_salary = format_number_with_spaces(salary)
        formatted_tax = format_number_with_spaces(tax)
        formatted_bonus = format_number_with_spaces(bonus)
    
        # Jadval satrini yaratish
        row = [
            Paragraph(str(year), custom_normal),
            Paragraph(month, custom_normal),
            Paragraph(company, custom_normal),  # "Enterprise (Organization)" column uchun Paragraph
            Paragraph(formatted_salary, custom_normal),
            Paragraph(formatted_tax, custom_normal),
            Paragraph(formatted_bonus, custom_normal),
        ]
    
        table_data.append(row)
    # Define column widths (adjusted for better spacing)

    col_widths = [
        15 * mm,  # Converted from 40 points
        23 * mm,  # Converted from 60.8 points
        64 * mm,  # Converted from 176.4 points
        24.40 * mm,  # Converted from 69.2 points
        24.27 * mm,  # Converted from 68.8 points
        35.89 * mm,  # Converted from 101.85 points
    ]

    # Create the table
    table = Table(table_data, colWidths=col_widths, hAlign="CENTER")

    # Define table styles
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.white),  # Header background
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),  # Header text color
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Center alignment for all cells
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # Vertical center alignment
                ("FONTNAME", (0, 0), (-1, 0), "CustomFontBold"),  # Header font
                ("FONTSIZE", (0, 0), (-1, 0), 10),  # Header font size
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),  # Header padding
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),  # Body background
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines
                ("FONTNAME", (0, 1), (-1, -1), "CustomFontReg"),  # Body font
                ("LEFTPADDING", (0, 0), (-1, -1), 10),  # Chapdan paddingni olib tashlash
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),  # O'ngdan paddingni olib tashlash
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("FONTSIZE", (0, 1), (-1, -1), 9),  # Body font size
            ]
        )
    )

    elements.append(table)

    elements.append(Spacer(1, (0.3 * inch)))
    qr_data = f"https://pincode-rose.vercel.app?id={objStr['_id']}"


    # QR kod yaratish
    qr = qrcode.QRCode(
        version=6,  # Kattaroq versiya tanlash (1-40 oralig'ida)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # O'xshash xatolarni to'g'rilash darajasi (H = yuqori)
        box_size=20,  # Har bir qutining o'lchamini kattalashtirish
        border=4,  # Chekka qirralarni kattalashtirish
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    # QR kodni rasmga aylantirish
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # QR kodni xotirada saqlash uchun BytesIO obyektini yaratish
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")  # QR kodni xotiraga PNG formatida saqlash
    qr_buffer.seek(0)  # Bufferning boshlanishiga qaytish

    footer = Paragraph(
        """This document is a copy of an electronic document generated in accordance with the
        provision on the Single Portal of Interactive Public Services, approved by the provision
        of the Cabinet of Ministers of the Republic of Uzbekistan dated September 15, 2017
        No. 728. To check the accuracy of the information specified in the copy of the
        electronic document, go to the website repo.gov.uz and enter the unique number of the
        electronic document, or scan the QR code using a mobile device. Attention! In
        accordance with the provision of the Cabinet of Ministers of the Republic of Uzbekistan
        dated September 15, 2017 No. 728, the information contained in electronic documents
        is legitimate. It is strictly forbidden for state bodies to refuse to accept copies of
        electronic documents generated on the Single Portal of Interactive Public Services.""",
        custom_normal_footer,
    )
   
    pin_code = Paragraph(str(objStr["pin"]), custom_normal_bold)
#    pin_code = Paragraph(f"{obj["pin"]}", custom_normal_bold)
    qr_code_img = Image(
        qr_buffer, width=1.2 * inch, height=1.2 * inch
    )  # QR kod rasm o'lchamini sozlash

    left_column_width = 5.28 * inch
    center_column_width = 0.8 * inch
    right_column_width = 1.2 * inch
    
    # Jadvalga QR kodni kiritish
    table3 = Table(
        [[footer, pin_code, qr_code_img]],
        colWidths=[left_column_width, center_column_width, right_column_width],
    )  # Har bir ustunning kengligi 50%

    table3.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                # ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]
        )
    )
    elements.append(table3)
    doc.build(
        elements,
        onFirstPage=lambda canvas, doc: add_page_number(canvas, doc, date_time="2024-10-08 14:22:00", line_color=colors.black, font_size=8),
        onLaterPages=lambda canvas, doc: add_page_number(canvas, doc, date_time="2024-10-08 14:22:00", line_color=colors.black, font_size=8)
    )
    # print(f"Final PDF with custom font created successfully: {output_path}")
    buffer.seek(0) 
    return buffer

# if __name__ == "__main__":
#         input_data = sys.stdin.read()  # Standard inputdan o'qish
#         # print(input_data)
#         response = create_final_pdf(input_data)  # Call the function to create the PDF
#         response.seek(0)  # Reset the buffer pointer to the beginning
#         pdf_data = response.read()  # Read the binary data from the buffer
#         response.close() 
#         #print(pdf_data)
#         sys.stdout.buffer.write(pdf_data)  # Write the binary PDF data to stdout
#         #print("Tugadi")
     
