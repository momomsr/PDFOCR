import io
import os
import signal
import threading
from typing import Callable, List, Optional

import streamlit as st
import pypdfium2 as pdfium
import easyocr
import numpy as np
from fpdf import FPDF
from fpdf.errors import FPDFException
import torch
import textwrap


# Prevent third-party module discovery mechanisms from inspecting
# ``torch.classes`` as a namespace package.  Some libraries walk through
# ``torch`` using ``pkgutil`` and attempt to examine ``torch.classes.__path__``,
# which triggers noisy error messages like::
#
#   Examining the path of torch.classes raised: Tried to instantiate class
#   '__path__._path', but it does not exist!
#
# Setting ``__path__`` to an empty list makes ``torch.classes`` appear as an
# empty namespace package and avoids the spurious warning.
if hasattr(torch, "classes"):
    try:
        torch.classes.__path__ = []  # type: ignore[attr-defined]
    except Exception:
        pass


# easyocr uses PyTorch's DataLoader with pin_memory=True by default, which
# triggers a warning and slows down execution when no accelerator (GPU/MPS)
# is available.  Monkey-patch DataLoader to disable pin_memory on CPU-only
# environments to avoid the warning observed by users.
if not torch.cuda.is_available():
    class _DataLoader(torch.utils.data.DataLoader):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("pin_memory", False)
            super().__init__(*args, **kwargs)

    torch.utils.data.DataLoader = _DataLoader


def _exit_on_sigint(sig, frame) -> None:
    """Terminate immediately on Ctrl+C."""
    os._exit(0)





def _pdf_to_images(pdf_bytes: bytes, dpi: int) -> List:
    """Render all PDF pages to PIL images using pdfium."""
    pdf = pdfium.PdfDocument(io.BytesIO(pdf_bytes))
    images: List = []
    for page in pdf:
        pil_image = page.render(scale=dpi / 72).to_pil()
        images.append(pil_image)
    return images


def ocr_pdf(
    pdf_bytes: bytes,
    lang: str,
    dpi: int,
    progress_cb: Optional[Callable[[float], None]] = None,
) -> bytes:
    """Run OCR on a PDF and return a new PDF containing only recognized text."""
    images = _pdf_to_images(pdf_bytes, dpi)
    easyocr_lang = lang[:2]
    reader = easyocr.Reader([easyocr_lang], gpu=False)
    all_text: List[str] = []
    total = len(images)
    for idx, img in enumerate(images, start=1):
        result = reader.readtext(np.array(img), detail=0, paragraph=True)
        text = "\n".join(result)
        all_text.append(text)
        if progress_cb:
            progress_cb(idx / total)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for page_text in all_text:
        pdf.add_page()
        # Determine maximum characters per line based on current page width
        max_chars = max(int(pdf.epw / pdf.get_string_width("W")), 1)
        for line in page_text.splitlines():
            wrapped_lines = textwrap.wrap(
                line,
                width=max_chars,
                break_long_words=True,
                break_on_hyphens=False,
            )
            for wrapped in wrapped_lines:
                try:
                    pdf.multi_cell(0, 8, wrapped)
                except FPDFException:
                    # Fallback: split into smaller chunks if rendering fails
                    for chunk in textwrap.wrap(wrapped, width=max_chars // 2 or 1):
                        pdf.multi_cell(0, 8, chunk)
    return pdf.output(dest="S").encode("latin-1")


def main() -> None:
    st.set_page_config(page_title="PDF OCR")
    st.title("PDF OCR App")
    st.write(
        "Die Applikation verarbeitet die Daten lokal auf dem Gerät, weshalb die Verarbeitung etwas dauern kann. Es wird nichts auf irgend einen Server hochgeladen."
    )

    uploaded = st.file_uploader("PDF-Datei hochladen", type="pdf")
    if uploaded:
        st.session_state["uploaded_pdf"] = uploaded.getvalue()

    lang = st.text_input("OCR-Sprache", value="de")
    dpi = st.slider("DPI für Bildkonvertierung", 72, 300, 200)

    if st.session_state.get("uploaded_pdf") and st.button("OCR starten"):
        progress_bar = st.progress(0)
        with st.spinner("Verarbeite..."):
            result_pdf = ocr_pdf(
                st.session_state["uploaded_pdf"],
                lang=lang,
                dpi=dpi,
                progress_cb=lambda p: progress_bar.progress(int(p * 100)),
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
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGINT, _exit_on_sigint)
    main()
