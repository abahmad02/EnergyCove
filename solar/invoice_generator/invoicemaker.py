# Import the required modules
import fpdf  # For creating pdf files
import PyPDF2
import datetime  # For getting the current date
import fitz 
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import math

def merge_pdfs(pdf_list, output_filename):
    merged_pdf = PyPDF2.PdfWriter()

    for pdf in pdf_list:
        with open(pdf, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in range(reader.numPages):
                merged_pdf.add_page(reader.getPage(page))

    with open(output_filename, 'wb') as f:
        merged_pdf.write(f)

def add_pdf_to_middle(existing_pdf, pdf_to_add, page_number, output_filename):
    merged_pdf = PyPDF2.PdfWriter()

    with open(existing_pdf, 'rb') as f1, open(pdf_to_add, 'rb') as f2:
        existing_reader = PyPDF2.PdfReader(f1)
        pdf_to_add_reader = PyPDF2.PdfReader(f2)

        for page in range(len(existing_reader.pages)):
            if page == page_number:
                for add_page in range(len(pdf_to_add_reader.pages)):
                    merged_pdf.add_page(pdf_to_add_reader.pages[add_page])
            merged_pdf.add_page(existing_reader.pages[page])

    with open(output_filename, 'wb') as f:
        merged_pdf.write(f)


    with open(output_filename, 'wb') as f:
        merged_pdf.write(f)


import fitz  # Import the PyMuPDF library

def replace_text(input_pdf, output_pdf, replacements, zoom_factor=3.0):
    # Open the existing PDF
    doc = fitz.open(input_pdf)

    # Perform text replacements
    for page in doc:
        for placeholder, replacement in replacements.items():
            text_instances = page.search_for(placeholder)
            for inst in text_instances:
                rect = fitz.Rect(inst[0], inst[1], inst[2], inst[3])
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                # Adjust the position for text insertion based on zoom_factor
                page.insert_text(rect.bottom_left, replacement, fontsize=int(16), overlay=True)

    # Create a new PDF
    c = canvas.Canvas(output_pdf, pagesize=letter)

    # Convert each page to an image at a higher resolution and add it to the new PDF
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)  # Load the current page
        mat = fitz.Matrix(zoom_factor, zoom_factor)  # Create a transformation matrix for the desired zoom
        pix = page.get_pixmap(matrix=mat)  # Render page with the transformation matrix

        with tempfile.NamedTemporaryFile(delete=True, suffix=".png") as tmpfile:
            pix.save(tmpfile.name)  # Save the pixmap to a temporary file
            img_width, img_height = pix.width, pix.height
            # Adjust page size based on zoomed image dimensions
            c.setPageSize((img_width / zoom_factor, img_height / zoom_factor))
            c.drawInlineImage(tmpfile.name, 0, 0, width=img_width / zoom_factor, height=img_height / zoom_factor)
            c.showPage()

    c.save()

    # Clean up
    doc.close()
    
def send_email_with_attachment(subject, body, to_email, attachment_path):
    from_email = "royaltaj.care@gmail.com"  # replace with your email
    from_password = "gxsd elyy djzb kldu"  # replace with your email password

    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # Open the file as binary mode
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode the file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to the attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {os.path.basename(attachment_path)}",
    )

    # Attach the attachment to the MIMEMultipart object
    msg.attach(part)

    # Create SMTP session for sending the mail
    server = smtplib.SMTP('smtp.gmail.com', 587)  # Use your SMTP server details
    server.starttls()  # enable security
    server.login(from_email, from_password)  # login with your email and password
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()
    

def generate_invoice(system_size, panel_amount, panel_power, price_of_inverter,
                     brand_of_inverter, price_of_panels, netmetering_costs,
                     installation_costs, cabling_costs, structure_costs,
                     electrical_and_mechanical_costs, total_cost, customer_name, customer_address, customer_contact):
    # Create a pdf object with modified document dimensions
    pdf = fpdf.FPDF(format=(260, 420))
    pdf.add_page()
    # Set the font and color
    pdf.set_font("Arial", size=20)
    pdf.set_text_color(0, 0, 0) 
    #total_cost = (panel_amount * price_of_panels) + price_of_inverter + netmetering_costs + installation_costs + cabling_costs + structure_costs + electrical_and_mechanical_costs
    advance_payment = float(total_cost) * 0.9
    # Add the header section
    pdf.cell(240, 10, txt="Energy Cove Solar System Invoice", ln=1, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(120, 10, txt=f"Customer Name: {customer_name}", ln=0, align="L")
    pdf.cell(120, 10, txt=f"Quotation Date: {datetime.date.today()}", ln=1, align="R")
    pdf.cell(120, 10, txt=f"Customer Address: {customer_address}", ln=0, align="L")
    pdf.cell(120, 10, txt=f"Present Date: {datetime.date.today()}", ln=1, align="R")
    pdf.cell(120, 10, txt=f"Customer Contact: {customer_contact}", ln=1, align="L")

    # Add the system size and type section
    pdf.set_fill_color(255, 255, 0)
    pdf.set_font("Arial", size=18)  
    
    pdf.cell(240, 10, txt=f"{system_size} kW | Solar System", ln=1, align="C",border=1, fill=True)

    # Add the description table
    pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Arial", size=12)
    pdf.cell(15, 10, txt="S.No", border=1, ln=0, align="C", fill=True)
    pdf.cell(190, 10, txt="Description", border=1, ln=0, align="C", fill=True)
    pdf.cell(15, 10, txt="QTY", border=1, ln=0, align="C", fill=True)
    pdf.cell(20, 10, txt="Price", border=1, ln=1, align="C", fill=True)

    pdf.cell(15, 30, txt="1", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 0)
    pdf.set_font("Arial", size=16)
    pdf.cell(190, 20, txt="PV Panels", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Arial", size=12)
    pdf.cell(15, 20, txt=f"{panel_amount}", border="L, R,T", ln=0, align="C", fill=True)
    pdf.cell(20, 20, txt=f"{price_of_panels}", border="L,R,T", ln=1, align="R", fill=True)  
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.cell(95, 10, txt=f"Brand: ", border=1, ln=0, align="L", fill=True)
    pdf.cell(95, 10, txt=f"Power Rating: {panel_power}", border=1, ln=0, align="L", fill=True)
    pdf.cell(15, 10, txt="", border="L,R,B")  # Empty cell to create space
    pdf.cell(20, 10, txt="", border="L,R,B", ln=1)  # Empty cell to create space


    pdf.cell(15, 40, txt="2", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 0)
    pdf.set_font("Arial", size=16)
    pdf.cell(190, 20, txt="Inverter & Accessories", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Arial", size=12)
    pdf.cell(15, 20, txt=f"", border="L, R, T", ln=0, align="C", fill=True)
    pdf.cell(20, 20, txt=f"", border="L,R, T", ln=1, align="R", fill=True)  
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.cell(63.3, 10, txt=f"Brand: {brand_of_inverter}", border=1, ln=0, align="L", fill=True)
    pdf.cell(63.3, 10, txt=f"Power Rating: {system_size}kW", border=1, ln=0, align="L", fill=True)
    pdf.cell(63.4, 10, txt=f"Model: On-Grid", border=1, ln=0, align="L", fill=True)
    pdf.cell(15, 10, txt="1", border="L,R", align="C")  # Empty cell to create space
    pdf.cell(20, 10, txt=f"{int(float(price_of_inverter))}", border="L,R", ln=1, align="R")  # Empty cell to create space
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.cell(190, 10, txt=f"Monitoring Device Included/ 5 Years warranty / System Produces 1200 Units per month", border=1, ln=0, align="L", fill=True)
    pdf.cell(15, 10, txt=f"", border="L, R,B", ln=0, align="C", fill=True)
    pdf.cell(20, 10, txt=f"", border="L,R,B", ln=1, align="R", fill=True)  

    pdf.cell(15, 40, txt="3", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 0)
    pdf.set_font("Arial", size=14)
    pdf.cell(190, 10, txt="DC Cable & Earthing", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Arial", size=12)
    pdf.cell(15, 10, txt=f"", border="L, R,T", ln=0, align="C", fill=True)
    pdf.cell(20, 10, txt=f"", border="L,R,T", ln=1, align="R", fill=True)  
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.cell(95, 10, txt="DC Cable: 1000 VDC, 4mm as required by design & PVC Conduits", border=1, ln=0, align="L", fill=True)
    pdf.cell(95, 10, txt="Protection Box with Circuit Breakers, Fuses", border=1, ln=0, align="L", fill=True)
    pdf.cell(15, 10, txt="1", border="L,R", ln=0, align="C", fill=True)
    pdf.cell(20, 10, txt=f"{cabling_costs}", border="L,R", ln=1, align="R", fill=True)
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.set_fill_color(255, 255, 0)
    pdf.set_font("Arial", size=14)
    pdf.cell(190, 10, txt="AC Cable", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Arial", size=12)
    pdf.cell(15, 10, txt=f"", border="L, R", ln=0, align="C", fill=True)
    pdf.cell(20, 10, txt=f"", border="L,R", ln=1, align="R", fill=True)  
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.cell(190, 10, txt="AC Cable: 0.415kV as per required design (10 Meter from Inverter to Main DB )", border=1, ln=0, align="L", fill=True)
    pdf.cell(15, 10, txt="", border="L,R,B", ln=0, align="C", fill=True)
    pdf.cell(20, 10, txt=f"", border="L,R,B", ln=1, align="R", fill=True)

    pdf.cell(15, 30, txt="4", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 0)
    pdf.set_font("Arial", size=16)
    pdf.cell(190, 20, txt="PV Panels Structure", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Arial", size=12)
    pdf.cell(15, 20, txt=f"1", border="L, R,T", ln=0, align="C", fill=True)
    pdf.cell(20, 20, txt=f"{int(float(structure_costs))}", border="L,R,T", ln=1, align="R", fill=True)  
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.cell(190, 10, txt=f"Customized frames with steel pipes & Chanels 14 guage and painting for 18 panels", border=1, ln=0, align="L", fill=True)
    pdf.cell(15, 10, txt="", border="L,R,B")  # Empty cell to create space
    pdf.cell(20, 10, txt="", border="L,R,B", ln=1)  # Empty cell to create space

    pdf.cell(15, 50, txt="5", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 0)
    pdf.set_font("Arial", size=16)
    pdf.cell(190, 20, txt="Balance of System / Installation & Commissioning", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Arial", size=12)
    pdf.cell(15, 20, txt=f"", border="L, R,T", ln=0, align="C", fill=True)
    pdf.cell(20, 20, txt=f"", border="L,R,T", ln=1, align="R", fill=True)  
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.cell(190, 10, txt=f"AC/DC Cable Trau, Flexible Pipes, Conduits, Rawal Bolts, Cable Ties, Lugs & other accessories", border=1, ln=0, align="L", fill=True)
    pdf.cell(15, 10, txt="1", border="L,R", align="C")  # Empty cell to create space
    pdf.cell(20, 10, txt=f"{int(float(installation_costs))}", border="L,R", ln=1, align="R")  # Empty cell to create space
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.cell(190, 10, txt=f"Transportation Cost", border=1, ln=0, align="L", fill=True)
    pdf.cell(15, 10, txt="", border="L,R")  # Empty cell to create space
    pdf.cell(20, 10, txt="", border="L,R", ln=1)  # Empty cell to create space
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.cell(190, 10, txt=f"Earthing system AC/DC", border=1, ln=0, align="L", fill=True)
    pdf.cell(15, 10, txt="", border="L,R,B")  # Empty cell to create space
    pdf.cell(20, 10, txt="", border="L,R,B", ln=1)  # Empty cell to create space

    pdf.cell(15, 30, txt="6", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 0)
    pdf.set_font("Arial", size=16)
    pdf.cell(190, 20, txt="Installation & Commissioning ", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Arial", size=12)
    pdf.cell(15, 20, txt=f"1", border="L, R,T", ln=0, align="C", fill=True)
    pdf.cell(20, 20, txt=f"{int(float(electrical_and_mechanical_costs))}", border="L,R,T", ln=1, align="R", fill=True)  
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.cell(190, 10, txt=f"Electrical & Mechanical work", border=1, ln=0, align="L", fill=True)
    pdf.cell(15, 10, txt="", border="L,R,B")  # Empty cell to create space
    pdf.cell(20, 10, txt="", border="L,R,B", ln=1)  # Empty cell to create space
    # Add the netmetering section
    pdf.cell(15, 40, txt="7", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 0)
    pdf.set_font("Arial", size=16)
    pdf.cell(190, 20, txt="Netmetering", border=1, ln=0, align="C", fill=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Arial", size=12)
    pdf.cell(15, 20, txt=f"", border="L, R,T", ln=0, align="C", fill=True)
    pdf.cell(20, 20, txt=f"", border="L,R,T", ln=1, align="R", fill=True)  
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.cell(95, 10, txt=f"Preparation of file - Dealing with MEPCO", border=1, ln=0, align="L", fill=True)
    pdf.cell(95, 10, txt=f"2 Reverse meters supply", border=1, ln=0, align="L", fill=True)
    pdf.cell(15, 10, txt="1", border="L,R" , align="C")  # Empty cell to create space
    pdf.cell(20, 10, txt=f"{int(float(netmetering_costs))}", border="L,R", ln=1, align="R")  # Empty cell to create space
    pdf.cell(15, 10, txt="", border=0)  # Empty cell to create space
    pdf.cell(190, 10, txt=f"Load extension / Main wire from green meters to Main DB of house in the scope of client", border=1, ln=0, align="L", fill=True)
    pdf.cell(15, 10, txt="", border="L,R,B")  # Empty cell to create space
    pdf.cell(20, 10, txt="", border="L,R,B", ln=1)  # Empty cell to create space
    # Add the total system cost section
    pdf.set_fill_color(0, 128, 0)
    pdf.set_font("Arial", size=15)
    pdf.cell(205, 20, txt=f"Total System Cost:",border=1, ln=0, align="C", fill=True)
    pdf.cell(35, 20, txt=f"{int(total_cost)}", border=1, ln=1, align="C", fill=True)
    pdf.cell(205, 20, txt=f"90% Advance Payment and 10% after testing commissioning:", border=1, ln=0, align="C", fill=True)
    pdf.cell(35, 20, txt=f"{int(advance_payment)}", border=1, ln=1, align="C", fill=True)


    def get_resource_path(relative_path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.realpath(__file__))

        return os.path.join(base_path, relative_path)

    # Use get_resource_path to find template.pdf correctly in both scenarios
    template_file = get_resource_path("template.pdf")
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    # Generate filename for the output PDF
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    output_pdf_filename = f"{date_time}_invoice.pdf"

    # Output the PDF (assuming you have a `pdf` object ready to be output)
    pdf.output(output_pdf_filename)
    print(f"PDF generated: {output_pdf_filename}")

    try:
        with open(template_file, 'rb') as file:
            # Assuming `add_pdf_to_middle` and other functions are correctly implemented
            print(f"Successfully opened {template_file}")
    except Exception as e:
        print(f"Could not open file: {e}")

    # Update the path for the generated invoice when calling your functions
    intermediate_pdf = f"{date_time}_with_pricing.pdf"
    customer_temp_name = customer_name.replace(" ", "_")
    final_pdf = f"{customer_temp_name}_{date_time}.pdf"

    # Add the modified PDF to the middle of the invoice.pdf file
    add_pdf_to_middle(template_file, output_pdf_filename, 2, intermediate_pdf)

    replacements = {
        "[NAME]": customer_name,
        "[System Power] KW [System Type ]PV System": f"{str(int(system_size))} KW | On-Grid PV System",
    }

    replacements_string = str(replacements)

    def get_user_folder_name():
        # Get the path to the user's home directory
        home_directory = os.environ.get('USERPROFILE')
        
        # Extract the folder name from the home directory path
        user_folder_name = os.path.basename(home_directory)
        
        return user_folder_name

    # Usage
    user_folder_name = get_user_folder_name()
    print(user_folder_name)

    output_file_path = f"C:/Users/{user_folder_name}/Documents/{final_pdf}"
    # Replace text in the final PDF
    # Replace text in the final PDF
    replace_text(intermediate_pdf, output_file_path, replacements)
    subject = "Your Invoice"
    body = "Please find your invoice attached."
    to_email = "abdullah123ahmad@gmail.com"  # replace with the customer's email

    send_email_with_attachment(subject, body, to_email, output_file_path)

    # Open the final PDF file
    