from flask import Flask, render_template, request, redirect
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
EXCEL_FILE = "contractor_data.xlsx"

DIA_COLUMNS = ["75 DIA", "90 DIA", "120 DIA", "140 DIA", "150 DIA", "180 DIA", "200 DIA", "220 DIA"]

# Initialize Excel with correct structure
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        "DATE", "VENDOR CODE", "NAME OF THE CONTRACTOR", "SCHEME ID", "PANCHAYAT", "TYPE"
    ] + DIA_COLUMNS)
    df.to_excel(EXCEL_FILE, index=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/details")
def details():
    return render_template("details.html")
@app.route("/submit", methods=["POST"])
def submit():
    contractor = request.form.get("contractorName")
    vendor_code = request.form.get("vendorCode")
    scheme_id = request.form.get("SchemeID")
    panchayat = request.form.get("panchayat")
    date = request.form.get("workDate")
    formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")

    # Ensure Excel file exists before reading
    if not os.path.exists(EXCEL_FILE):
        df_init = pd.DataFrame(columns=[
            "DATE", "VENDOR CODE", "NAME OF THE CONTRACTOR", "SCHEME ID", "PANCHAYAT", "TYPE"
        ] + DIA_COLUMNS)
        df_init.to_excel(EXCEL_FILE, index=False)
    else:
        df = pd.read_excel(EXCEL_FILE)
        df.columns = df.columns.str.strip().str.upper()

    cumulative_row = {
        "DATE": formatted_date,
        "VENDOR CODE": vendor_code,
        "NAME OF THE CONTRACTOR": contractor,
        "SCHEME ID": scheme_id,
        "PANCHAYAT": panchayat,
        "TYPE": "cumulative_sum"
    }
    previous_row = {
        "DATE": "",
        "VENDOR CODE": "",
        "NAME OF THE CONTRACTOR": "",
        "SCHEME ID": "",
        "PANCHAYAT": "",
        "TYPE": "previous_sum"
    }
    bill_row = {
        "DATE": "",
        "VENDOR CODE": "",
        "NAME OF THE CONTRACTOR": "",
        "SCHEME ID": "",
        "PANCHAYAT": "",
        "TYPE": "this_bill"
    }

    for dia_label in DIA_COLUMNS:
        dia_value = dia_label.split()[0]
        form_key = f"bill_{dia_value}"
        dia_col = dia_label.upper().strip()

        if form_key in request.form:
            try:
                bill = int(request.form[form_key])
            except ValueError:
                bill = 0
            if dia_col not in df.columns:
                df[dia_col] = 0

            mask = (
                (df["VENDOR CODE"] == vendor_code) &
                (df["NAME OF THE CONTRACTOR"] == contractor) &
                (df["TYPE"] == "this_bill")
            )
            prev_total = df.loc[mask, dia_col].sum() if dia_col in df.columns else 0

            cumulative_row[dia_col] = prev_total + bill
            previous_row[dia_col] = prev_total
            bill_row[dia_col] = bill
        else:
            cumulative_row[dia_col] = 0
            previous_row[dia_col] = 0
            bill_row[dia_col] = 0

    df = pd.concat([df, pd.DataFrame([cumulative_row, previous_row, bill_row])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

   
    return redirect("/")
if __name__ == "__main__":
    app.run(debug=True)
