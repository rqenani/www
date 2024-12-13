
from flask import Flask, request, jsonify
import os
import pdfplumber
import re

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def process_pdf(filepath):
    rows = []
    total_row = {}
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split("\n")
            for line in lines:
                if re.match(r"\d+\s+[A-Z].*\d{2,}", line):
                    parts = line.split()
                    if len(parts) >= 7:
                        rows.append({
                            "ID": parts[0],
                            "Emri": " ".join(parts[1:-5]),
                            "Paga Bruto": float(parts[-4].replace(",", "")),
                            "Kontributet": float(parts[-3].replace(",", "")),
                            "TAP": float(parts[-1].replace(",", ""))
                        })
                if "Totali i Listepageses" in line:
                    numbers = re.findall(r"\d+[,\.]?\d*", line)
                    if len(numbers) >= 3:
                        total_row = {
                            "Paga Bruto": float(numbers[0].replace(",", "")),
                            "Kontributet": float(numbers[1].replace(",", "")),
                            "TAP": float(numbers[2].replace(",", ""))
                        }
    return rows, total_row

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    rows, total_row = process_pdf(filepath)
    return jsonify({"employees": rows, "totals": total_row})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
