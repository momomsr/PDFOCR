import io
from typing import List

import streamlit as st
import pypdfium2 as pdfium
import pytesseract
from fpdf import FPDF


def _pdf_to_images(pdf_bytes: bytes, dpi: int) -> List:
    """Render all PDF pages to PIL images using pdfium."""
    pdf = pdfium.PdfDocument(io.BytesIO(pdf_bytes))
    images: List = []
    for page in pdf:
        pil_image = page.render(scale=dpi / 72).to_pil()
        images.append(pil_image)
    return images


def ocr_pdf(pdf_bytes: bytes, lang: str, psm: int, dpi: int) -> bytes:
    """Run OCR on a PDF and return a new PDF containing only recognized text."""
    images = _pdf_to_images(pdf_bytes, dpi)
    all_text: List[str] = []
    config = f"--psm {psm}"
    for img in images:
        text = pytesseract.image_to_string(img, lang=lang, config=config)
        all_text.append(text)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for page_text in all_text:
        pdf.add_page()
        for line in page_text.splitlines():
            pdf.multi_cell(0, 8, line)
    return pdf.output(dest="S").encode("latin-1")


def main() -> None:
    st.set_page_config(page_title="PDF OCR")
    st.title("PDF OCR App")

    uploaded = st.file_uploader("PDF-Datei hochladen", type="pdf")
    if uploaded:
        st.session_state["uploaded_pdf"] = uploaded.getvalue()

    lang = st.text_input("OCR-Sprache", value="deu")
    psm = st.selectbox(
        "Seiten-Layout-Erkennung (PSM)",
        options=list(range(0, 14)),
        index=3,
        format_func=lambda x: f"PSM {x}"
    )
    dpi = st.slider("DPI für Bildkonvertierung", 72, 300, 200)

    if st.session_state.get("uploaded_pdf") and st.button("OCR starten"):
        with st.spinner("Verarbeite..."):
            result_pdf = ocr_pdf(
                st.session_state["uploaded_pdf"],
                lang=lang,
                psm=psm,
                dpi=dpi,
            )
            st.session_state["processed_pdf"] = result_pdf
            st.success("OCR abgeschlossen!")

    if st.session_state.get("processed_pdf"):
        st.download_button(
            "OCR-Ergebnis herunterladen",
            st.session_state["processed_pdf"],
            file_name="ocr_result.pdf",
            mime="application/pdf",
        )


if __name__ == "__main__":
    main()
