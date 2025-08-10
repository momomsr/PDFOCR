import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import pytesseract
from pdf2image import convert_from_path
from io import BytesIO

def pdf_to_images(pdf_file):
    images = convert_from_path(pdf_file, dpi=300)
    return images

def images_to_text(images):
    text_pages = []
    for image in images:
        text = pytesseract.image_to_string(image, lang='eng')
        text_pages.append(text)
    return text_pages

def create_text_pdf(text_pages):
    output = BytesIO()
    writer = PdfWriter()
    for page_text in text_pages:
        writer.add_blank_page(width=612, height=792)  # Standard page size
        writer.pages[-1].insert_text(page_text)
    writer.write(output)
    output.seek(0)
    return output

st.title("PDF OCR App")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
if uploaded_file:
    st.info("Processing the uploaded PDF file...")

    # Convert PDF to images
    images = pdf_to_images(uploaded_file)
    
    # Extract text from images using OCR
    extracted_text = images_to_text(images)

    # Create a new PDF with extracted text
    output_pdf = create_text_pdf(extracted_text)

    # Provide the processed PDF for download
    st.download_button(label="Download OCR Processed PDF", 
                       data=output_pdf, 
                       file_name="processed_text.pdf", 
                       mime="application/pdf")

    st.success("Processing complete! You can now download the processed PDF.")