# PDF OCR

Dieses Projekt bietet eine kleine [Streamlit](https://streamlit.io)-Anwendung, um PDF-Dateien mit Hilfe der Open-Source-OCR-Engine [Tesseract](https://github.com/tesseract-ocr/tesseract) zu verarbeiten. Hochgeladene PDFs werden seitenweise in Bilder umgewandelt, per OCR erkannt und als neue PDF mit extrahiertem Text zum Download bereitgestellt.

## Voraussetzungen

- Python 3.10 oder neuer
- Systempakete [`tesseract-ocr`](https://tesseract-ocr.github.io/tessdoc/Home.html) und [`poppler-utils`](https://poppler.freedesktop.org/) (werden für die Bildkonvertierung benötigt)

## Installation

1. Optional: Virtuelle Umgebung anlegen
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Abhängigkeiten installieren
   - Linux/macOS:
     ```bash
     bash install.sh
     ```
   - Windows:
     ```
     install.bat
     ```

Alternativ können die Python-Abhängigkeiten auch manuell installiert werden:
```bash
pip install -r requirements.txt
```

## Anwendung starten

Nach erfolgreicher Installation lässt sich die Anwendung mit Streamlit starten:
```bash
streamlit run app.py
```
Streamlit zeigt anschließend die lokale URL, unter der die Weboberfläche aufgerufen werden kann.

## Hinweise

- Die Sprache für die Texterkennung (Standard: Deutsch) sowie der PSM-Modus und die DPI lassen sich in der Benutzeroberfläche anpassen.
- Für eine korrekte OCR müssen die entsprechenden Sprachpakete von Tesseract installiert sein (z. B. `tesseract-ocr-deu`).
