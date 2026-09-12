import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_invoice_pdf(transaction):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
    )

    bold_label = ParagraphStyle(
        'BoldLabel',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1e293b')
    )

    normal_text = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Header section
    story.append(Paragraph("FREELANCIFY", title_style))
    story.append(Paragraph("Official Platform Invoice & Escrow Receipt", subtitle_style))
    story.append(Spacer(1, 20))

    # Invoice Metadata Table
    meta_data = [
        [Paragraph("Invoice Number:", bold_label), Paragraph(f"#{str(transaction.invoice_number)[:8].upper()}", normal_text)],
        [Paragraph("Date Issued:", bold_label), Paragraph(transaction.created_at.strftime('%B %d, %Y'), normal_text)],
        [Paragraph("Payment Status:", bold_label), Paragraph(transaction.get_status_display(), normal_text)],
        [Paragraph("Contract ID:", bold_label), Paragraph(f"#{transaction.contract.id}", normal_text)],
    ]

    t_meta = Table(meta_data, colWidths=[120, 400])
    t_meta.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 20))

    # Parties Section
    parties_data = [
        [Paragraph("CLIENT (PAID BY)", bold_label), Paragraph("FREELANCER (PAYEE)", bold_label)],
        [
            Paragraph(f"<b>{transaction.payer.get_full_name() or transaction.payer.username}</b><br/>Email: {transaction.payer.email}<br/>Role: Client", normal_text),
            Paragraph(f"<b>{transaction.payee.get_full_name() or transaction.payee.username}</b><br/>Email: {transaction.payee.email}<br/>Title: {transaction.payee.profile.title}", normal_text)
        ]
    ]

    t_parties = Table(parties_data, colWidths=[260, 260])
    t_parties.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(t_parties)
    story.append(Spacer(1, 25))

    # Line items table
    item_header = [Paragraph("Description", bold_label), Paragraph("Amount", bold_label)]
    item_row = [
        Paragraph(f"<b>Job Title:</b> {transaction.contract.job.title}<br/><i>{transaction.description}</i>", normal_text),
        Paragraph(f"${transaction.amount:.2f}", bold_label)
    ]
    
    items_table_data = [item_header, item_row]

    t_items = Table(items_table_data, colWidths=[400, 120])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(t_items)
    story.append(Spacer(1, 30))

    # Total Section
    summary_data = [
        [Paragraph("Total Paid / Encumbered:", bold_label), Paragraph(f"<b>${transaction.amount:.2f} USD</b>", title_style)]
    ]
    t_summary = Table(summary_data, colWidths=[300, 220])
    t_summary.setStyle(TableStyle([
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 40))

    # Footer
    story.append(Paragraph("Thank you for using Freelancify! If you have any billing questions, contact support@freelancify.com", subtitle_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
