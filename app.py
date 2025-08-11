import io
import os
from pathlib import Path
from typing import List, Optional

import streamlit as st
from pdf2image import convert_from_bytes
from pdf2image.exceptions import PDFInfoNotInstalledError
import pytesseract
from fpdf import FPDF


def _detect_poppler_path() -> Optional[str]:
    """Try to locate the poppler binaries.

    Returns the path to the poppler "bin" directory if found, otherwise
    ``None``. On Windows a couple of common installation locations (including
    the default Chocolatey path) are checked in addition to the optional
    ``POPPLER_PATH`` environment variable.
    """

    env_path = os.environ.get("POPPLER_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    if os.name == "nt":
        candidates = [
            r"C:\\Program Files\\poppler\\bin",
            r"C:\\Program Files (x86)\\poppler\\bin",
            r"C:\\ProgramData\\chocolatey\\lib\\poppler\\tools",
        ]
        for path in candidates:
            if Path(path).exists():
                return path

    return None


def ocr_pdf(pdf_bytes: bytes, lang: str, psm: int, dpi: int) -> bytes:
    """Run OCR on a PDF and return a new PDF containing only recognized text."""
    poppler_path = _detect_poppler_path()
    try:
        images = convert_from_bytes(pdf_bytes, dpi=dpi, poppler_path=poppler_path)
    except PDFInfoNotInstalledError as exc:
        raise RuntimeError(
            "Poppler konnte nicht gefunden werden. Bitte installieren und den Pfad\n"
            "über die Umgebungsvariable POPPLER_PATH angeben."
        ) from exc
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
