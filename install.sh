#!/usr/bin/env bash
set -e

# Systemabhängigkeiten installieren
sudo apt-get update
sudo apt-get install -y tesseract-ocr

# Python-Abhängigkeiten installieren
pip install --upgrade pip
pip install -r requirements.txt
