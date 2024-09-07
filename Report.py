# Required libraries
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
import os

# Required system files
import Style

# Store incoming titles and subtiltes
title_list = []
chapter_list = []


# Used to create the static title page (template)
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
    
    elements.append(title_para)
    elements.append(Spacer(1, 40))  # Add space after the title
    elements.append(subtitle_para)
    elements.append(Spacer(1, 20))  # Add space after the subtitle
    elements.append(abstract_para)
    elements.append(PageBreak())
    
    return elements


# Generate the table of content in the end of the state machine
def build_table_of_contents():
    elements = []
    styles = Style.getSampleStyleSheet()

    table_of_contents_para = Paragraph('Table of Contents', style=styles['Heading2'])

    elements.append(table_of_contents_para)
    elements.append(Spacer(1, 10))  # Add space after the title

    index = 0

    # Load all titles and chapters into the document

    for indexitem in range(0, len(title_list)):
        index += 1
        entry_para = Paragraph((str(indexitem+1) + '.\t' + title_list[indexitem]), style=styles['Heading3'])
        elements.append(entry_para)
        
        subindex = 0
        for chapter in chapter_list[indexitem]:        
            subindex += 1
            subentry_para = Paragraph((str(indexitem+1) + "." + str(subindex) + "\t" + chapter), style=styles['Heading4'])
            elements.append(subentry_para)

        elements.append(Spacer(1, 5))  # Add space after the subtitle
    
    elements.append(PageBreak())

    return elements

# Most important function here:
# Used to generate documentation from a Report job
def build_document(data, insertPageBreakAfter):
    elements = []

    # Get the default stylesheet
    styles = getSampleStyleSheet()
    topic_style = styles['Heading2']
    headline_style = styles['Heading3']

    # Define a custom paragraph style for table cells to handle word wrap
    cell_style = ParagraphStyle('cell_style', parent=styles['Normal'], wordWrap=True)

    # Print each chapter title only one time
    if data['title'] not in title_list:
        title_list.append(data['title'])
        title_text = str(title_list.index(data['title']) + 1) + '. ' + str(data['title'])
        title = Paragraph(title_text, topic_style)
        elements.append(title)
        elements.append(Spacer(1, 12))  # Add space after the title

    # Process each key in the data dictionary
    for key, value in data['data'].items():
        # Ensure chapter_list has enough sublists
        while len(chapter_list) <= title_list.index(data['title']):
            chapter_list.append([])

        if key not in chapter_list[title_list.index(data['title'])]:
            chapter_list[title_list.index(data['title'])].append(key)

        # Add the key as a heading
        title_index = str(title_list.index(data['title']) + 1)
        heading_index = str(chapter_list[title_list.index(data['title'])].index(key) + 1)
        heading = Paragraph(f"<b>{title_index + '.' + heading_index + ' ' + key}</b>", headline_style)

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
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), True),  # Enable word wrap for all cells
        ])

        # Zeilen prüfen und ggf. rot einfärben
        for i, row in enumerate(table_data):
            if any(isinstance(cell, Paragraph) and ("Response (OK)" in cell.text) for cell in row):
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.green)
                table_style.add('TEXTCOLOR', (0, i), (-1, i), colors.whitesmoke)
            if any(isinstance(cell, Paragraph) and ("Response (ERROR)" in cell.text) for cell in row):
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.red)
                table_style.add('TEXTCOLOR', (0, i), (-1, i), colors.whitesmoke) 
            if any(isinstance(cell, Paragraph) and ("Response (TIMEOUT)" in cell.text) for cell in row):
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.yellow)
                table_style.add('TEXTCOLOR', (0, i), (-1, i), colors.whitesmoke)   

        # Tabelle mit Stil anwenden
        table.setStyle(table_style)

        # Add the table to the elements
        elements.append(table)
        elements.append(Spacer(1, 12))  # Add space after the table

    # If specified, add a PageBreak
    if insertPageBreakAfter:
        elements.append(PageBreak())

    # Build the PDF
    return elements

# Final report generation
def render_document(data, filename):
    # Add all entries of the document list to the document
    document = []
    for entry in data:
        document.extend(entry)

     # Set document settings
    pdf = SimpleDocTemplate(
        filename=filename, 
        pagesize=letter,
        rightMargin=72, 
        leftMargin=72,
        topMargin=72, 
        bottomMargin=72
    )
    
    # Generate PDF document finally
    pdf.build(document)

    return 0