# 🧪 Medical Lab Report Data Extraction using PaddleOCR

This project is a lightweight Python server built to **extract structured data from medical lab reports** using **PaddleOCR**, with a focus on privacy and local processing. It enables integration with telehealth systems or other healthcare platforms.

---

## 🚀 Features

- 🖼️ Supports image and PDF lab report uploads
- 🧠 Uses PaddleOCR to extract text from scanned documents
- 🗂️ Extracts and structures key medical data (e.g., test name, value, reference range)
- 🔐 Designed for local/private deployment for privacy-sensitive healthcare use cases
- 📦 REST API for easy integration

---

## 🏗️ Tech Stack

- **Python 3.8+**
- **Flask** – lightweight server
- **PaddleOCR** – text extraction
- **pdf2image** – for PDF conversion
- **Pillow**, **OpenCV**, etc.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/senthamizht/lab-report-data-extraction.git
cd lab-report-data-extraction

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
