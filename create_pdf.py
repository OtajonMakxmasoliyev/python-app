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
    canvas.drawString(7.59 * inch, 0.38 * inch, f"{page_number}")
    
    # If date_time is provided, draw it at the top-right position
    if date_time:
        canvas.drawString(6.5 * inch, 11.23 * inch, date_time)
    
    # Set the stroke color dynamically using the provided argument
    canvas.setStrokeColor(line_color)
    canvas.setLineWidth(0.5)  # Set the line width
    
    # Draw lines at the bottom and top of the page
    line_length = 7.09 * inch  # Set the line length to 7.09 inches
    
    # Bottom line (aligned horizontally with 0.60 inch from the left and line_length from there)
    canvas.line(0.58 * inch, 0.5 * inch, 0.60 * inch + line_length, 0.5 * inch)
    
    # Top line (aligned the same way, just at the top of the page)
    canvas.line(0.58 * inch, 11.18 * inch, 0.60 * inch + line_length, 11.18 * inch)


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


def draw_content_borders(canvas, doc):
    """ Draws borders for the content area within the margins. """
    # Margins
    left_margin = 0.60 * inch
    right_margin = 0.60 * inch
    top_margin = 50 * mm
    bottom_margin = 50 * mm

    # Page dimensions
    PAGE_WIDTH, PAGE_HEIGHT = A4

    # Calculate the coordinates for the content area
    content_x1 = left_margin
    content_y1 = bottom_margin
    content_x2 = PAGE_WIDTH - right_margin
    content_y2 = PAGE_HEIGHT - top_margin

    # Draw the borders
    canvas.setStrokeColor(colors.grey)  # Set border color
    canvas.setLineWidth(0.5)  # Set border line width

    # Draw the rectangle for the content area
    canvas.rect(content_x1, content_y1, content_x2 - content_x1, content_y2 - content_y1)


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
        rightMargin=0.60 * inch,
        leftMargin=0.60 * inch,
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
        fontSize=0.1458333 * inch,
        leading=12,
        wordWrap="CJK",  # Enables word wrapping
        alignment=TA_CENTER,  # Matnni markazga hizalash
    )
    custom_normal_footer = ParagraphStyle(
        name="CustomNormal",
        parent=styles["Normal"],
        fontName="CustomFontReg",
        fontSize=9,
        leading=9,
        wordWrap="CJK",  # Enables word wrapping
        alignment=TA_JUSTIFY,  # Matnni markazga hizalash
    )

    custom_normal_bold = ParagraphStyle(
        name="CustomNormal",
        parent=styles["Normal"],
        fontName="CustomFontReg",
        fontSize=(22.5 / 72) * inch,
        leading=12,
        wordWrap="CJK",  # Enables word wrapping
        alignment=TA_CENTER,  # Matnni markazga hizalash
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
    custom_normal_left_remove = ParagraphStyle(
        name="CustomNormal",
        parent=styles["Normal"],
        fontName="CustomFontReg",
        fontSize=9,
        leading=12,
        leftIndent=0,  # 0 px left indent
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
        fontSize=0.1458333 * inch,
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
        fontSize=0.1458333 * inch,
        leading=14,
        spaceBefore=0,  # 0 px space before
        spaceAfter=0,  # 0 px space after
        # 0 px left indent
        rightIndent=0,  # 0 px right indent
        leftIndent=-8,  # 0 px right indent
        firstLineIndent=0,  # 0 px first line indent
        alignment=TA_LEFT,  # Chapga hizalanish
        textColor=colors.HexColor("#333333"),  # Matn rangi
    )
    para1 = Paragraph("Single Portal of Interactive Public Services", deja_serif_bold)

    # 2. Image (Rasm)
    image_path = "./image/logo.png"  # Rasm faylini to'g'ri yo'lga o'zgartiring
    if os.path.exists(image_path):
        logo = Image(image_path)
        logo.drawWidth = 1.2 * inch
        logo.drawHeight = 1.2 * inch
    else:
        logo = Paragraph("Rasm topilmadi", custom_normal)

    gov_image = "./image/gov_logo.png"
    if os.path.exists(gov_image):
        gov_logo = Image(gov_image)
        gov_logo.drawHeight = 9 * mm
        gov_logo.drawWidth = 39.5 * mm
    else:
        gov_logo = Paragraph("Rasm topilmadi", custom_normal)

    # 3. Ikkinchi Paragraph
    para2 = [
        Paragraph("The State", custom_center_style),
        Paragraph("Tax Committee", custom_center_style),
        Paragraph("of the", custom_center_style),
        Paragraph("Uzbekistan", custom_center_style),
    ]

    # Jadval ma'lumotlari (Uchta Elementni Yonma-Yon Qo'yish)
    table_data = [[[gov_logo, para1], logo, para2]]
    PAGE_WIDTH, PAGE_HEIGHT = A4

    available_width = PAGE_WIDTH
    # Ustunlar uchun foizlar (umumiy 100%)
    col_percentages = [28, 27, 37]  # Foizlarni kerakli miqdorga moslang

    # Har bir ustunning kengligini hisoblash
    col_widths = [available_width * (percent / 100) for percent in col_percentages]

    # Jadvalni yaratish
    table = Table(table_data, colWidths=col_widths, hAlign="CENTER")  # HAlign "CENTER" qilib qo'ydik

    # Jadval uslublari
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # Vertikal markazlashtirish
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Gorizontal markazlashtirish
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),  # Pastki padding
                # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Agar kerak bo'lsa, tarmoq chizig'i
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, (0.5 * inch)))

    # Add document details
    detail1 = [
        f"№ {obj['id']}",
        f"Document creation date: {convert_timestamp(obj['createdAt'])}",
        f"Application number: {obj['applicationNumber']}",
    ]
    detail2 = [
        f"Document issued: {obj['fullName'].upper()}",
        f"PINFL: {obj['pnfl']}",
    ]

    formatted_detail1 = [Paragraph(detail1[0], custom_normal_left_remove)]
    formatted_detail2 = [Paragraph(detail2[0], custom_normal_right)]

    # detail1 va detail2 ni formatlash
    for i in range(1, len(detail1)):
        formatted_detail1.append(Paragraph(detail1[i], custom_normal_left_remove))

    for i in range(1, len(detail2)):
        formatted_detail2.append(Paragraph(detail2[i], custom_normal_right))

    # Har bir ustun uchun kengliklarni hisoblash
    left_column_width = (available_width - 75) * 0.5  # Chap ustun uchun 50%
    right_column_width = (available_width - 80) * 0.5  # O'ng ustun uchun 50%

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
    elements.append(table2)  # Har bir elementni chapdan chiqarish uchun "deja_sans_left" uslubini qo'llaymiz
    elements.append(Spacer(1, (0.5 * inch)))
    elements.append(Paragraph("INCOME STATEMENT", deja_sans))  # Chapdan hizalanadi
    elements.append(Spacer(0, (0.51 * inch)))

    # Foydalanuvchi to'liq ismini ko'rsatish
    elements.append(Paragraph(f"Name: {obj['fullName'].upper()}", deja_sans_left))  # Chapdan hizalanadi
    elements.append(Paragraph("TIN:", deja_sans_left))  # Chapdan hizalanadi
    elements.append(Paragraph(f"PRSA: {obj['pnfl']}", deja_sans_left))  # Chapdan hizalanadi
    elements.append(Spacer(2, 0.51 * inch))
    elements.append(
        Paragraph(
            "Issued in that the above person has received the following income:",
            deja_sans_left,  # Chapdan hizalanadi
        )
    )
    elements.append(Spacer(2, 0.11 * inch))

    # Umumiy daromad va soliqni hisoblash
    total_salary = 0
    total_tax = 0
    for salary_entry in obj["salaries"]:
        salary = salary_entry['salary']
        tax = salary_entry['tax']
        if salary:
            salary = int(salary)  # MongoDB Extended JSON formatini tekshirish
        else:
            salary = 0
        total_salary += salary

        if tax:
            tax = int(tax)  # MongoDB Extended JSON formatini tekshirish
        else:
            tax = 0
        total_tax += tax

    # Umumiy daromad va soliqni ko'rsatish
    elements.append(Paragraph(f"Total estimated salary: {format_number_with_spaces(total_salary)}", deja_sans_left))  # Chapdan hizalanadi
    elements.append(Spacer(2, 0.28 * inch))

    elements.append(Paragraph(f"Income tax: {format_number_with_spaces(total_tax)}", deja_sans_left))  # Chapdan hizalanadi
    elements.append(Spacer(1.5, 0.44 * inch))

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
        0.50 * inch,  # Converted from 40 points
        0.85 * inch,  # Converted from 60.8 points
        2.18 * inch,  # Converted from 176.4 points
        1.21 * inch,  # Converted from 69.2 points
        1.16 * inch,  # Converted from 68.8 points
        1.20 * inch,  # Converted from 101.85 points
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
                # ("LEFTPADDING", (0, 0), (-1, -1), 15),  # Chapdan paddingni olib tashlash
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
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
        border=0,  # Chekka qirralarni 0 qilib qo'yamiz
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    # QR kodni rasmga aylantirish
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # QR kodni xotirada saqlash uchun BytesIO obyektini yaratish
    qr_buffer = BytesIO()

    # QR kodning o'lchamini 1.03 inch ga o'rnatish
    target_size = 1.03 * inch  # O'lchovlarni belgilash

    # QR kodni ko'rsatish va kenglik va balandlikni o'rnatish
    qr_img = qr_img.resize((int(target_size), int(target_size)))

    qr_img.save(qr_buffer, format="PNG")  # QR kodni xotiraga PNG formatida saqlash
    qr_buffer.seek(0)  #
    footer_style = ParagraphStyle(
        name="FooterStyle",
        fontName="CustomFontReg",  # O'zingizga kerakli font nomini qo'yishingiz mumkin
        fontSize=9,  # Font o'lchami
        leading=9,  # Qator balandligi
        textColor=colors.HexColor("#333333"),  # Matn rangi
        parent=styles["Normal"],
        # wordWrap="CJK",  # Enables word wrapping
        alignment=TA_JUSTIFY,
    )
    footer = Paragraph(
        "This document is a copy of an electronic document generated in accordance with the provision on the Single Portal of Interactive Public Services, approved by the provision of the Cabinet of Ministers of the Republic of Uzbekistan dated September 15, 2017 No. 728. To check the accuracy of the information specified in the copy of the electronic document, go to the website repo.gov.uz and enter the unique number of the electronic document, or scan the QR code using a mobile device. Attention! In accordance with the provision of the Cabinet of Ministers of the Republic of Uzbekistan dated September 15, 2017 No. 728, the information contained in electronic documents is legitimate. It is strictly forbidden for state bodies to refuse to accept copies of electronic documents generated on the Single Portal of Interactive Public Services.",
        footer_style,
        )
   
    pin_code = Paragraph(str(objStr["pin"]), custom_normal_bold)
#    pin_code = Paragraph(f"{obj["pin"]}", custom_normal_bold)
    qr_code_img = Image(
        qr_buffer, width=1.03 * inch, height=1.03 * inch
    )  # QR kod rasm o'lchamini sozlash

    left_column_width = 5.15 * inch
    center_column_width = 0.94 * inch
    right_column_width = 1.05 * inch
    
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
        onFirstPage=lambda canvas, doc: [
            add_page_number(canvas, doc, date_time="2024-10-08 14:22:00", line_color=colors.black, font_size=8),
            # draw_content_borders(canvas, doc)  # Chegaralarni chizish
        ],
        onLaterPages=lambda canvas, doc: [
            add_page_number(canvas, doc, date_time="2024-10-08 14:22:00", line_color=colors.black, font_size=8),
            # draw_content_borders(canvas, doc)  # Chegaralarni chizish
        ]
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
     
