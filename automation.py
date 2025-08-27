#!/usr/bin/env python3
"""
Placeholder automation script invoked after the user enters the kit number.

This script retrieves the previously uploaded and analysed data using the
temporary key passed from the analysis page. It then reads the kit number
provided by the user. In a complete implementation this step would
instantiate a Playwright browser, log into the CAP site, locate the
appropriate result form using the kit number, and fill in values for
specimens and analytes according to the data provided. Due to limitations
in the execution environment (missing dependencies and headless browser
drivers), this script simply displays a confirmation page showing
the kit number and basic information about the data. It illustrates
where automation would normally occur.
"""
import cgi
import cgitb
import json
import os
import sys
import tempfile

from upload import load_temp_data

cgitb.enable()

def main():
    form = cgi.FieldStorage()
    kit_number = form.getfirst("kit_number", "").strip()
    data_key = form.getfirst("data_key", "").strip()
    if not kit_number or not data_key:
        print("Content-type: text/html\n")
        print("<h1>Missing parameters</h1>")
        return
    # Load previously stored data
    try:
        data = load_temp_data(data_key)
    except Exception as exc:
        print("Content-type: text/html\n")
        print(f"<h1>Error loading data</h1><p>{str(exc)}</p>")
        return
    specimen_count = len({row[data["sample_column"]] for row in data["records"]})
    analyte_count = len(data["analyte_columns"])
    record_count = len(data["records"])
    # Display confirmation page
    print("Content-type: text/html\n")
    print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Automation Start</title>
<style>
    body {{ font-family: Arial, sans-serif; background-color: #f5f9fc; margin: 0; padding: 0; }}
    header {{ background-color: #2f59a6; color: #fff; padding: 20px; }}
    main {{ max-width: 800px; margin: 0 auto; padding: 30px; }}
    .card {{ background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    .card h2 {{ margin-top: 0; }}
    .btn {{ display: inline-block; padding: 10px 20px; background-color: #2563eb; color: #fff; border-radius: 4px; text-decoration: none; margin-top: 20px; }}
</style>
</head>
<body>
<header>
    <h1>Automation Initiated</h1>
</header>
<main>
    <div class="card">
        <h2>Kit Number: {kit}</h2>
        <p>The system would now log into the CAP portal and populate the result form for kit number <strong>{kit}</strong>.</p>
        <p><strong>Specimens:</strong> {specimens}</p>
        <p><strong>Analytes:</strong> {analytes}</p>
        <p><strong>Total Records:</strong> {records}</p>
        <p>Due to environment limitations the automated data entry is not executed in this demonstration.</p>
        <a class="btn" href="/">Return to Home</a>
    </div>
</main>
</body>
</html>
""".format(
        kit=cgi.escape(kit_number),
        specimens=specimen_count,
        analytes=analyte_count,
        records=record_count,
    ))


if __name__ == "__main__":
    main()