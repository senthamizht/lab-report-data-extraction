from paddleocr import PaddleOCR
from pprint import pprint
from PIL import Image
import sys
import re
import json
import os
import json
import csv
from pdf2image import convert_from_path
import numpy as np

ocr = PaddleOCR(use_angle_cls=True, lang='en')

def parse_lab_report(ocr_text: str):
    print(ocr_text)
    lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
    
    patient_info = {
        "name": "",
        "age": "",
        "sex": "",
        "pid": ""
    }

    report_info = {
        "collected_on": "",
        "reported_on": "",
        "generated_on": "",
        "ref_by": "",
        "sample_location": "",
        "instrument": ""
    }

    test_results = []
    
    # Extract patient & report info
    for i, line in enumerate(lines):
        if not patient_info["name"] and "pathology" in line.lower():
            patient_info["name"] = line
        if "Age" in line and not patient_info["age"]:
            match = re.search(r'Age\s*[:\-]?\s*(\d+)', line)
            if match:
                patient_info["age"] = match.group(1)
        if "Sex" in line and not patient_info["sex"]:
            match = re.search(r'Sex\s*[:\-]?\s*(\w+)', line)
            if match:
                patient_info["sex"] = match.group(1)
        if "PID" in line and not patient_info["pid"]:
            match = re.search(r'PID\s*[:\-]?\s*(\d+)', line)
            if match:
                patient_info["pid"] = match.group(1)
        if "Collected on" in line:
            report_info["collected_on"] = line.split("Collected on:")[-1].strip()
        if "Reported on" in line:
            report_info["reported_on"] = line.split("Reported on:")[-1].strip()
        if "Generated on" in line:
            report_info["generated_on"] = line.split("Generated on")[-1].strip(": ")
        if "Ref. By" in line:
            report_info["ref_by"] = line.split("Ref. By:")[-1].strip()
        if "Instruments" in line:
            report_info["instrument"] = line.strip()
        if "Sample Collected At" in line and i + 1 < len(lines):
            report_info["sample_location"] = lines[i + 1].strip()

    # Extract test results with units
    i = 0
    while i < len(lines) - 1:
        line = lines[i]
        next_line = lines[i + 1]

        # Detect a numeric value as result
        if re.fullmatch(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", next_line):
            test_name = line
            result = next_line
            unit = ""
            ref_range = ""
            flag = "Normal"

            # Check next line for Low/High flag and ref range
            if i + 2 < len(lines):
                third_line = lines[i + 2].strip()
                if re.search(r"(Low|High)", third_line, re.IGNORECASE) or re.search(r"\d+\s*-\s*\d+", third_line):
                    if "low" in third_line.lower():
                        flag = "Low"
                        third_line = re.sub(r'(?i)low', '', third_line).strip()
                    elif "high" in third_line.lower():
                        flag = "High"
                        third_line = re.sub(r'(?i)high', '', third_line).strip()
                    if re.search(r"\d+\s*-\s*\d+", third_line):
                        ref_range = third_line
                    i += 1  # consumed line

            # Check for unit on the line after ref_range
            if i + 2 < len(lines):
                possible_unit = lines[i + 2].strip()
                if re.match(r'^[a-zA-Z/%μ]+$', possible_unit) or re.search(r'[a-zA-Z]', possible_unit):
                    unit = possible_unit
                    i += 1

            test_results.append({
                "test_name": test_name,
                "result": result,
                "unit": unit,
                "ref_range": ref_range,
                "flag": flag
            })

            i += 2  # move past test_name and result
        else:
            i += 1

    return {
        "patient_info": patient_info,
        "report_info": report_info,
        "test_results": test_results
    }

def extract_text_from_image(image: Image.Image):
    image_np = np.array(image)
    result = ocr.ocr(image_np, cls=True)
    lines = []
    for block in result:
        for line in block:
            lines.append(line[1][0])
    return "\n".join(lines)

def extract_text_from_pdf(pdf_path: str):
    pages = convert_from_path(pdf_path)
    full_text = ""
    for page in pages:
        full_text += extract_text_from_image(page) + "\n"
    return full_text

def extract_text_from_csv(csv_path: str):
    lines = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 4:
                # Assuming row = [Test Name, Result, Unit, Ref Range, (optional) Flag]
                test_name = row[0].strip()
                result = row[1].strip()
                unit = row[2].strip() if len(row) > 2 else ""
                ref_range = row[3].strip() if len(row) > 3 else ""
                flag = row[4].strip() if len(row) > 4 else "Normal"

                lines.extend([
                    test_name,
                    result,
                    unit,
                    ref_range,
                    flag
                ])
            else:
                # Just flatten remaining rows as-is
                lines.extend([cell.strip() for cell in row if cell.strip()])
    return "\n".join(lines)

def extract_text_from_file(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".jpg", ".jpeg", ".png"]:
        return extract_text_from_image(Image.open(file_path).convert("RGB"))
    elif ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".csv":
        print('extracting from csv file');
        return extract_text_from_csv(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
    
def extract_data_from_file(file_path: str):
    # Parse results
    file_path = "medical_report.jpg"  # change to .pdf or .csv as needed

    print("Running OCR and extracting text...")
    ocr_text = extract_text_from_file(file_path)

    # print(ocr_text)

    print("Parsing extracted text into structured JSON...")
    parsed_json = parse_lab_report(ocr_text)

    # print("===== Final Output =====")
    # print(json.dumps(parsed_json, indent=2))
    return parsed_json
