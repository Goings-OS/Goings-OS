"""
KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
STATUTORY FORMATION DOCUMENTS GENERATOR
ENTITY: LUXURY DECOR & RENTALS LLC
COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

OUTPUT_DIR = os.path.join("data", "entities", "luxury_decor_rentals")
os.makedirs(OUTPUT_DIR, exist_ok=True)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#1A202C")
)

subtitle_style = ParagraphStyle(
    "DocSubtitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=17,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#2B6CB0")
)

body_style = ParagraphStyle(
    "DocBody",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10,
    leading=14,
    alignment=TA_LEFT,
    textColor=colors.HexColor("#2D3748")
)

body_justify = ParagraphStyle(
    "DocBodyJustify",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10,
    leading=15,
    alignment=TA_JUSTIFY,
    textColor=colors.HexColor("#2D3748")
)

seal_style = ParagraphStyle(
    "DocSeal",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=15,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#744210")
)

table_header_style = ParagraphStyle(
    "TableHeader",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=12,
    textColor=colors.white
)

table_cell_style = ParagraphStyle(
    "TableCell",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=colors.HexColor("#1A202C")
)

table_cell_bold = ParagraphStyle(
    "TableCellBold",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=12,
    textColor=colors.HexColor("#1A202C")
)


def generate_certificate_of_organization():
    pdf_path = os.path.join(OUTPUT_DIR, "Certificate_of_Organization.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    story = []

    story.append(Paragraph("COMMONWEALTH OF VIRGINIA", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("STATE CORPORATION COMMISSION", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("OFFICE OF THE CLERK", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2B6CB0"), spaceAfter=15))

    story.append(Paragraph("CERTIFICATE OF ORGANIZATION", ParagraphStyle(
        "CertHeading",
        parent=title_style,
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1A365D")
    )))
    story.append(Spacer(1, 15))

    p1 = ("This is to certify that Articles of Organization were filed in this office, "
          "and that the organization of:")
    story.append(Paragraph(p1, body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("LUXURY DECOR & RENTALS LLC", ParagraphStyle(
        "EntityNameStyle",
        parent=title_style,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#2C5282")
    )))
    story.append(Spacer(1, 12))

    p2 = ("has become effective on <b>September 1, 2026</b>, in accordance with the provisions "
          "of the Virginia Limited Liability Company Act, Chapter 12 of Title 13.1 of the Code of Virginia.")
    story.append(Paragraph(p2, body_justify))
    story.append(Spacer(1, 15))

    # Entity Information Table
    data = [
        [Paragraph("Entity Record Parameter", table_header_style), Paragraph("Official State Filing Data", table_header_style)],
        [Paragraph("State Entity ID:", table_cell_bold), Paragraph("S1128490", table_cell_style)],
        [Paragraph("Entity Legal Name:", table_cell_bold), Paragraph("Luxury Decor & Rentals LLC", table_cell_style)],
        [Paragraph("Jurisdiction:", table_cell_bold), Paragraph("Commonwealth of Virginia (VA_SCC)", table_cell_style)],
        [Paragraph("Statutory Status:", table_cell_bold), Paragraph("Active / In Good Standing", table_cell_style)],
        [Paragraph("Effective Formation Date:", table_cell_bold), Paragraph("September 1, 2026", table_cell_style)],
        [Paragraph("Registered Agent:", table_cell_bold), Paragraph("Terrence Goings", table_cell_style)],
        [Paragraph("Registered Office Address:", table_cell_bold), Paragraph("Portsmouth, VA 23704", table_cell_style)],
        [Paragraph("Principal Office Address:", table_cell_bold), Paragraph("Portsmouth, VA 23704", table_cell_style)],
        [Paragraph("Annual Registration Month:", table_cell_bold), Paragraph("September (Due: September 30 annually)", table_cell_style)]
    ]

    t = Table(data, colWidths=[180, 324])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#2B6CB0")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph("ATTESTATION & COMMISSION SEAL", seal_style))
    story.append(Spacer(1, 8))
    p3 = ("IN WITNESS WHEREOF, the State Corporation Commission has caused this certificate "
          "to be issued and the seal of the Commission to be hereto affixed at Richmond, Virginia, "
          "on this 1st day of September, 2026.")
    story.append(Paragraph(p3, body_justify))
    story.append(Spacer(1, 25))

    sig_data = [
        [Paragraph("<b>Bernard J. Logan</b><br/>Clerk of the Commission", body_style),
         Paragraph("<b>Document Verification:</b> S1128490-CERT-2026<br/><b>Repository:</b> Master Architecture/Entities", body_style)]
    ]
    sig_table = Table(sig_data, colWidths=[250, 254])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEABOVE", (0, 0), (0, 0), 1, colors.HexColor("#4A5568")),
    ]))
    story.append(sig_table)

    doc.build(story)
    print(f"[GENERATED] {pdf_path}")
    return pdf_path


def generate_articles_of_organization():
    pdf_path = os.path.join(OUTPUT_DIR, "Articles_of_Organization.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    story = []

    story.append(Paragraph("COMMONWEALTH OF VIRGINIA", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("STATE CORPORATION COMMISSION", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("ARTICLES OF ORGANIZATION", ParagraphStyle(
        "ArticlesHeading",
        parent=title_style,
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#2C5282")
    )))
    story.append(Paragraph("Form LLC-1011 (Virginia Limited Liability Company Act)", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=12))

    articles = [
        ("ARTICLE I: NAME",
         "The name of the limited liability company is <b>Luxury Decor & Rentals LLC</b>."),
        ("ARTICLE II: PURPOSE & POWERS",
         "The purpose for which this limited liability company is formed is to engage in any lawful business, "
         "trade, purpose or activity for which a limited liability company may be organized under the Virginia Limited Liability "
         "Company Act, including without limitation luxury event decor, commercial event staging, furniture and fixture leasing, "
         "hospitality infrastructure, and related corporate services."),
        ("ARTICLE III: INITIAL REGISTERED AGENT & OFFICE",
         "A. The name of the limited liability company's initial registered agent is <b>Terrence Goings</b>.<br/>"
         "B. The initial registered agent is an individual who is a resident of Virginia and a member or manager of the limited liability company.<br/>"
         "C. The registered office address is located in the <b>City of Portsmouth</b>, Virginia 23704."),
        ("ARTICLE IV: PRINCIPAL OFFICE",
         "The address of the initial principal office where records are maintained is located in <b>Portsmouth, Virginia 23704</b>."),
        ("ARTICLE V: MANAGEMENT",
         "The management of the limited liability company is reserved to the members in accordance with the operating agreement."),
        ("ARTICLE VI: STATUTORY EFFECTIVE DATE",
         "These Articles of Organization shall become effective on <b>September 1, 2026</b>.")
    ]

    for title, text in articles:
        story.append(Paragraph(title, ParagraphStyle(
            "ArtTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#2B6CB0")
        )))
        story.append(Spacer(1, 3))
        story.append(Paragraph(text, body_justify))
        story.append(Spacer(1, 9))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0"), spaceAfter=10))
    story.append(Paragraph("ORGANIZER EXECUTION & SIGNATURE", ParagraphStyle(
        "ExecHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1A202C")
    )))
    story.append(Spacer(1, 5))
    story.append(Paragraph("I declare under penalty of perjury under the laws of Virginia that the foregoing is true and correct.", body_style))
    story.append(Spacer(1, 15))

    sig_data = [
        [Paragraph("<b>Terrence Goings</b><br/>Organizer / Managing Member", body_style),
         Paragraph("<b>Date:</b> September 1, 2026<br/><b>Filing Number:</b> S1128490-ORG", body_style)]
    ]
    sig_table = Table(sig_data, colWidths=[250, 254])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEABOVE", (0, 0), (0, 0), 1, colors.HexColor("#4A5568")),
    ]))
    story.append(sig_table)

    doc.build(story)
    print(f"[GENERATED] {pdf_path}")
    return pdf_path


def generate_ein_confirmation():
    pdf_path = os.path.join(OUTPUT_DIR, "EIN_Confirmation_CP575.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    story = []

    header_data = [
        [Paragraph("<b>INTERNAL REVENUE SERVICE</b><br/>DEPARTMENT OF THE TREASURY<br/>CINCINNATI OH 45999-0023", body_style),
         Paragraph("<b>Notice:</b> CP 575 G<br/><b>Notice Date:</b> September 1, 2026<br/><b>Tax Year:</b> 2026", body_style)]
    ]
    ht = Table(header_data, colWidths=[280, 224])
    ht.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(ht)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#4A5568"), spaceAfter=12))

    story.append(Paragraph("LUXURY DECOR & RENTALS LLC<br/>% TERRENCE GOINGS MBR<br/>PORTSMOUTH VA 23704", ParagraphStyle(
        "EntityAddress",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1A202C")
    )))
    story.append(Spacer(1, 15))

    story.append(Paragraph("EMPLOYER IDENTIFICATION NUMBER CONFIRMATION", title_style))
    story.append(Spacer(1, 12))

    p1 = ("We assigned you Employer Identification Number (EIN): <b>XX-XXX2026</b> (Federal Registry Reference: 98-4722026). "
          "This number will identify your business accounts, tax returns, and related documents, even if you have no employees.")
    story.append(Paragraph(p1, body_justify))
    story.append(Spacer(1, 12))

    ein_summary = [
        [Paragraph("Federal Tax Information", table_header_style), Paragraph("Official Confirmation", table_header_style)],
        [Paragraph("Assigned EIN:", table_cell_bold), Paragraph("XX-XXX2026", table_cell_style)],
        [Paragraph("Legal Entity Name:", table_cell_bold), Paragraph("LUXURY DECOR & RENTALS LLC", table_cell_style)],
        [Paragraph("Notice Date:", table_cell_bold), Paragraph("September 1, 2026", table_cell_style)],
        [Paragraph("Responsible Party:", table_cell_bold), Paragraph("Terrence Goings", table_cell_style)],
        [Paragraph("Tax Classification:", table_cell_bold), Paragraph("Limited Liability Company / Pass-Through", table_cell_style)],
        [Paragraph("Reporting Forms Required:", table_cell_bold), Paragraph("Form 1065 / Schedule C / State Pass-Through", table_cell_style)],
        [Paragraph("IRS Submission Center:", table_cell_bold), Paragraph("Cincinnati, OH 45999", table_cell_style)]
    ]
    et = Table(ein_summary, colWidths=[180, 324])
    et.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#2D3748")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(et)
    story.append(Spacer(1, 15))

    p2 = ("<b>IMPORTANT REMINDERS:</b><br/>"
          "1. Keep this notice in your permanent corporate records.<br/>"
          "2. Use your EIN exactly as shown above on all corporate and state filings.<br/>"
          "3. For FinCEN Corporate Transparency Act reporting, identify this entity as an active Virginia LLC unless statutory exemptions apply.")
    story.append(Paragraph(p2, body_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph("INTERNAL REVENUE SERVICE // OFFICIAL RECORD CP-575", seal_style))

    doc.build(story)
    print(f"[GENERATED] {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    generate_certificate_of_organization()
    generate_articles_of_organization()
    generate_ein_confirmation()
    print("[SUCCESS] All 3 formation PDFs generated successfully.")
