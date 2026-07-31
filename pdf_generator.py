from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from database_functions import get_invoice_data
from reportlab.lib import colors
import numpy as np
import os
from datetime import date
from config import YOUR_NAME, YOUR_ADDRESS, YOUR_PHONE, YOUR_EMAIL, YOUR_ABN, YOUR_BANK, YOUR_BSB, YOUR_ACC, BASE_PATH, BASE_PATH_LAPTOP

def format_date(date_str):
    d = date.fromisoformat(date_str)
    return d.strftime("%d/%m/%Y")

def get_financial_year(issue_date_str):
    d = date.fromisoformat(issue_date_str)
    if d.month >= 7:
        return f"FY{d.year}-{str(d.year + 1)[2:]}"
    else:
        return f"FY{d.year - 1}-{str(d.year)[2:]}"                 

def generate_invoice_pdf(invoice_code, output_path=None):

    rows = get_invoice_data(invoice_code)
    if not rows:
        print(f"No data found for invoice {invoice_code}")
        return
    
    name        = rows[0][0]
    address     = rows[0][1]
    email       = rows[0][2]
    phone       = rows[0][3]
    inv_code    = rows[0][4]
    issue_date  = rows[0][5]
    due_date    = rows[0][6]

    parts = name.split()
    first, last = parts[0], parts[-1]
    fy = get_financial_year(issue_date)

    folder = os.path.join(BASE_PATH_LAPTOP, fy, "Invoices", f"INV_{first}_{last}")
    os.makedirs(folder, exist_ok=True)

    if output_path is None:
        output_path = os.path.join(folder, f"Invoice_{inv_code}.pdf")
        
    # --- styles ---
    bold   = ParagraphStyle("bold",   fontName="Helvetica-Bold",   fontSize=9)
    normal = ParagraphStyle("normal", fontName="Helvetica",         fontSize=9)
    small  = ParagraphStyle("small",  fontName="Helvetica",         fontSize=8)
    center = ParagraphStyle("center", fontName="Helvetica-Bold",    fontSize=14, alignment=TA_CENTER)
    right  = ParagraphStyle("right",  fontName="Helvetica",         fontSize=9,  alignment=TA_RIGHT)
    bold_right = ParagraphStyle("bold_right", fontName="Helvetica-Bold", fontSize=9, alignment=TA_RIGHT)

    story = []

    # --- header: your details left, invoice info right ---
    header_left = [
        Paragraph(f"{YOUR_NAME}", bold),
        Paragraph(f"Address: {YOUR_ADDRESS}", normal),
        Paragraph(f"Phone: {YOUR_PHONE}", normal),
        Paragraph(f"Email: {YOUR_EMAIL}", normal),
        
    ]
    header_right = [
        Paragraph(f"Invoice Date: {format_date(issue_date)}", right),
        Paragraph(f"Due Date: {format_date(due_date)}", right),
        Paragraph(f"ABN: {YOUR_ABN}", right),
        
    ]

    header_table = Table(
        [[header_left, header_right]],
        colWidths=[11*cm, 8*cm])
    
    header_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))

    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 10))

    # --- TAX INVOICE heading ---
    story.append(Paragraph(f"TAX INVOICE #{inv_code}", center))
    story.append(Spacer(1, 14))

    # --- client block ---
    story.append(Paragraph(name,    bold))
    story.append(Paragraph(address, normal))
    story.append(Paragraph(f"Phone: {phone}", normal))
    story.append(Paragraph(f"Email: {email}", normal))
    story.append(Spacer(1, 18))

    # --- line items table ---
    page_width = A4[0] - 2*cm  # total usable width
    col_widths = [2*cm, 11.4*cm, 1.8*cm, 1.8*cm, 2.2*cm]

    items_data = [["Date", "Description", "Hours", "Rate", "Amount"]]
    total = 0.0
    for row in rows:
        item_date   = row[7]
        description = row[8]
        quantity    = float(row[9])
        rate        = float(row[10])
        amount      = float(row[11])
        total      += amount
        items_data.append([
            format_date(item_date),
            description,
            f"{quantity:.2f}",
            f"{rate:.2f}",
            f"{amount:.2f}"
        ])
    
    
            # add empty rows to fill space (matches the look in your screenshot)
    #while len(items_data) < 6:
        #items_data.append(["", "", "", ""])

    items_data.append(["Subtotal", "", "", "", f"${total:.2f}"])
    items_data.append(["Total", "", "", "", f"${total:.2f}"])

    items_table = Table(items_data, colWidths=col_widths, hAlign="RIGHT")
    items_table.setStyle(TableStyle([
        # header row
        ("FONTNAME",    (0,0),  (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0),  (-1,-1), 9),
        ("BACKGROUND",  (0,0),  (-1,0),  colors.white),
        # borders
    
        # total rows — no left/middle borders, just text
        ("FONTNAME",    (3,-1), (-1,-1), "Helvetica-Bold"),
        ("ALIGN",       (2,1),  (4,-1),  "CENTER"),
        ("VALIGN",      (0,0),  (-1,-1), "MIDDLE"),
        ("TOPPADDING",  (0,0),  (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        #("LINEABOVE", (0,-2), (-1,-2), 1, colors.black),
        ("SPAN",     (0,-2), (3,-2)),   # merge cols 0-3 on subtotal row
        ("SPAN",     (0,-1), (3,-1)),   # merge cols 0-3 on total row
        ("ALIGN",    (0,-2), (0,-1),  "RIGHT"),   # right-justify the merged cell text
        ("ALIGN",    (4,-2), (4,-1),  "CENTER"),   # right-justify the amount
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),  # bold total row
        ("FONTNAME", (0,-2), (-1,-2), "Helvetica"),

        ("INNERGRID",   (0,0),  (-1,-3), 0.75, colors.black),
        ("LINEABOVE",   (0,0),  (-1,0),  0.75, colors.black),  # top edge
        ("LINEBELOW",   (0,-3), (-1,-3), 0.75, colors.black),  # bottom of item rows
        ("LINEBEFORE",  (0,0),  (0,-1),  0.75, colors.black),  # left edge
        ("LINEAFTER",   (-1,0), (-1,-1), 0.75, colors.black),  # right edge
        ("LINEABOVE",   (0,-2), (-1,-2), 0.75, colors.black),  # above subtotal
        ("LINEABOVE",   (0,-1), (-1,-1), 0.75, colors.black),  # above total
        ("LINEBEFORE",  (4,-2), (4,-1),  0.75, colors.black),  # separator in totals
        ("BOX",         (0,0),  (-1,-1), 0.75, colors.black),
            ]))


    story.append(items_table)
    story.append(Spacer(1, 14))
   
     # --- bank details bottom left ---
    bank_data = [
        [Paragraph("Bank Account Details", bold)],
        [Paragraph(f"Bank: {YOUR_BANK}", normal)],
        [Paragraph(f"Acc Holder Name: {YOUR_NAME.upper()}", normal)],
        [Paragraph(f"BSB: {YOUR_BSB}", normal)],
        [Paragraph(f"ACC: {YOUR_ACC}", normal)],
    ]
    bank_table = Table(bank_data)
    bank_table.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0), (-1,-1), 0),
        ("BOTTOMPADDING",(0,0), (-1,-1), 2),
    ]))
    story.append(bank_table)

    SimpleDocTemplate(output_path, pagesize = letter,
                  rightMargin = 1*cm, leftMargin = 1*cm,
                  topMargin= 2*cm, bottomMargin=1*cm).build(story)
    
    print(f"Invoice saved to {output_path}")
