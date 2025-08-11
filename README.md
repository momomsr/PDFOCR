# PDF OCR

Dieses Projekt bietet eine kleine [Streamlit](https://streamlit.io)-Anwendung, um PDF-Dateien mit Hilfe der reinen Python-Bibliothek [EasyOCR](https://github.com/JaidedAI/EasyOCR) zu verarbeiten. Hochgeladene PDFs werden seitenweise in Bilder umgewandelt, per OCR erkannt und als neue PDF mit extrahiertem Text zum Download bereitgestellt.

## Voraussetzungen

- Python 3.10 oder neuer


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

## Debug-Modus

Zum Debuggen kann ein Modus aktiviert werden, der die Roh-Ergebnisse der OCR in der Konsole protokolliert und Bilder mit den erkannten Bounding-Boxes abspeichert.

- Linux/macOS:
  ```bash
  OCR_DEBUG=1 streamlit run app.py
  ```
- Windows (PowerShell):
  ```powershell
  $env:OCR_DEBUG=1
  streamlit run app.py
  ```

Die Debug-Bilder werden als `debug_page_<nummer>.png` im aktuellen Verzeichnis abgelegt.

## Hinweise

- Die Sprache für die Texterkennung (Standard: Deutsch) sowie die DPI lassen sich in der Benutzeroberfläche anpassen.
- EasyOCR erwartet ISO-639-1 Sprachcodes (z. B. `de` für Deutsch, `en` für Englisch).
- Während der Verarbeitung zeigt ein Ladebalken den Fortschritt der Konvertierung an.
- Das Programm kann jederzeit über `Strg+C` in der Kommandozeile beendet werden.
