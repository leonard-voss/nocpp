
#   For PDF merging only
from PyPDF2 import PdfReader, PdfWriter

#   For PDF generator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph


title_list = []

#   For interaction with the file system
import os

# Stylesheet for reports
import Style

def merge_pdfs(self, report_pdf_name, pdf_to_add, delete_after_merge):
    # Schritt 1: Öffnen der bestehenden Report-PDF
    reader1 = PdfReader(report_pdf_name)
    
    # Schritt 2: Öffnen der PDF, die hinzugefügt werden soll
    reader2 = PdfReader(pdf_to_add)
    
    # Schritt 3: Erstellen eines PDF-Writers
    writer = PdfWriter()
    
    # Schritt 4: Hinzufügen aller Seiten der bestehenden Report-PDF
    for page_num in range(len(reader1.pages)):
        page = reader1.pages[page_num]
        writer.add_page(page)
    
    # Schritt 5: Hinzufügen aller Seiten der PDF, die hinzugefügt werden soll
    for page_num in range(len(reader2.pages)):
        page = reader2.pages[page_num]
        writer.add_page(page)
    
    # Schritt 6: Speichern der kombinierten PDF unter dem ursprünglichen Report-PDF-Namen
    with open(report_pdf_name, 'wb') as output_file:
        writer.write(output_file)
    
    # Schritt 7: Löschen der ursprünglichen PDF, falls gewünscht
    if delete_after_merge:
        os.remove(pdf_to_add)


# Used to create the cover sheet and the table of contents
def build_template(title, subtitle, software_version):
    elements = []
    styles = Style.getSampleStyleSheet()

    title_style = Style.ParagraphStyle(
        'Title',
        parent=styles['Title'],
        textColor=colors.purple
    )

    abstract = """
        This application is used to identify vulnerabilities in the OCPP charging point 
        protocol. The aim of the application is information gathering and the detection 
        of vulnerabilities that indicate a faulty implementation of the protocol in the 
        charging station. For example, the behavior is tested for fuzzing 
        (sending deliberately false data).
    """

    title_para = Paragraph(str('TEST REPORT'), style=title_style)
    subtitle_para = Paragraph((title + " (" + subtitle + ")"), style=styles['Heading1'])
    abstract_para = Paragraph(str(abstract), style=styles['Normal'])
    table_of_contents_para = Paragraph('Table of Contents', style=styles['Heading2'])
    
    elements.append(title_para)
    elements.append(Spacer(1, 40))  # Add space after the title
    elements.append(subtitle_para)
    elements.append(Spacer(1, 20))  # Add space after the subtitle
    elements.append(abstract_para)
    elements.append(Spacer(1, 40))  # Add space after the subtitle
    elements.append(table_of_contents_para)
    elements.append(Spacer(1, 10))  # Add space after the title
    
    content = {
        'Configuration': ['General', 'WebSocket'],
        'Information Gathering': ['BootNotification', 'StatusNotification', 'GetConfiguration']
    }

    index = 0

    for key, value in content.items():
        index += 1
        entry_para = Paragraph((str(index) + '.\t' + key), style=styles['Heading3'])
        elements.append(entry_para)
        subindex = 0
        for subentry in value:
            subindex += 1
            subentry_para = Paragraph((str(index) + "." + str(subindex) + "\t" + subentry), style=styles['Heading4'])
            elements.append(subentry_para)
        elements.append(Spacer(1, 5))  # Add space after the subtitle

    elements.append(PageBreak())
    
    return elements


def build_document(data, insertPageBreakAfter):
    elements = []

    # Get the default stylesheet
    styles = getSampleStyleSheet()
    topic_style = styles['Heading2']
    headline_style = styles['Heading3']

    # Define a custom paragraph style for table cells to handle word wrap
    cell_style = ParagraphStyle('cell_style', parent=styles['Normal'], wordWrap=True)

    # Add the title as a heading
    title = Paragraph(data['title'], topic_style)

    # Print each chapter title only one time.
    if data['title'] not in title_list:
        title_list.append(data['title'])
        elements.append(title)
        elements.append(Spacer(1, 12))  # Add space after the title

    # Process each key in the data dictionary
    for key, value in data['data'].items():
        # Add the key as a heading
        heading = Paragraph(f"<b>{key}</b>", headline_style)
        elements.append(heading)
        elements.append(Spacer(1, 12))  # Add space after the heading

        # Prepare data for the table
        table_data = []
        for row in value:
            formatted_row = [
                Paragraph(str(cell), cell_style) if isinstance(cell, (str, bool)) else str(cell)
                for cell in row
            ]
            table_data.append(formatted_row)

        # Calculate total width of the table
        available_width = letter[0] - 144  # Total width minus left and right margin (assuming 1 inch margin)
        num_cols = len(table_data[0]) if table_data else 0
        col_widths = [available_width / num_cols] * num_cols if num_cols > 0 else []

        # Create the table with calculated column widths
        table = Table(table_data, colWidths=col_widths)

        # Add a table style with word wrap
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), True),  # Enable word wrap for all cells
        ]))

        # Add the table to the elements
        elements.append(table)
        elements.append(Spacer(1, 12))  # Add space after the table

    if insertPageBreakAfter:
        elements.append(PageBreak())

    # Build the PDF
    return elements

def render_document(data, filename):
    
    document = []

    for entry in data:
        document.extend(entry)

     # Create a PDF document with margins
    pdf = SimpleDocTemplate(
        filename=filename, 
        pagesize=letter,
        rightMargin=72, 
        leftMargin=72,
        topMargin=72, 
        bottomMargin=72
    )
    
    pdf.build(document)

    return 0
