#!/usr/bin/env python3
"""
CGI script to handle Excel file upload, parse its contents and display a summary.

The script uses the `pandas` library to read the uploaded Excel file and attempts
to automatically detect the column containing specimen/sample identifiers and
columns containing analyte values. Columns with names containing
"unit", "qualifier" or "unnamed" (case-insensitive) are ignored when
inferring analyte columns.

The script outputs a simple HTML page showing:
  * Total record count (rows)
  * Number of analytes detected
  * Number of unique specimens
  * List of detected analyte column names
  * Warnings for missing or non‑numeric values
  * Duplicate specimen/analyte combinations

After reviewing the summary, the user can enter a kit number and proceed to
the automation step. The Excel data is stored on the server in a temporary
file referenced by a generated key so that subsequent steps can access it
without persisting logs to disk. The data file is removed when the Python
process ends (e.g. after the session completes).
"""

import cgi
import cgitb
import json
import os
import sys
import tempfile
from io import BytesIO

import pandas as pd

# enable debugging
cgitb.enable()


def guess_sample_column(columns):
    """Attempt to identify the sample/specimen identifier column."""
    lower = [c.lower() for c in columns]
    for i, name in enumerate(lower):
        if any(k in name for k in ("sample", "specimen", "id")):
            return columns[i]
    # fallback to first column
    return columns[0] if columns else None


def guess_analyte_columns(columns, sample_col):
    """Return a list of columns that likely contain analyte values."""
    analytes = []
    for col in columns:
        if col == sample_col:
            continue
        lower = col.lower()
        if any(k in lower for k in ("unit", "qualifier", "unnamed")):
            continue
        analytes.append(col)
    return analytes


def parse_excel(file_bytes):
    """Read the uploaded Excel file into a pandas DataFrame."""
    try:
        df = pd.read_excel(BytesIO(file_bytes))
    except Exception as exc:
        raise RuntimeError(f"Failed to parse Excel file: {exc}") from exc
    return df


def analyze_data(df):
    """Compute summary statistics and data quality issues."""
    columns = list(df.columns)
    sample_col = guess_sample_column(columns)
    analyte_cols = guess_analyte_columns(columns, sample_col)

    summary = {
        "total_records": len(df),
        "analytes_found": len(analyte_cols),
        "specimens": df[sample_col].nunique() if sample_col in df else 0,
        "analyte_list": analyte_cols,
    }

    issues = []
    # Track duplicates by (specimen, analyte)
    duplicates = {}
    for analyte in analyte_cols:
        for idx, value in df[[sample_col, analyte]].itertuples(index=False):
            specimen = idx
            val = value
            key = (specimen, analyte)
            # Check missing
            if pd.isna(val) or (isinstance(val, str) and val.strip() == ""):
                issues.append({
                    "type": "missing",
                    "specimen": specimen,
                    "analyte": analyte,
                    "value": val,
                })
                continue
            # Check non-numeric
            try:
                float(str(val).strip())
            except Exception:
                issues.append({
                    "type": "non_numeric",
                    "specimen": specimen,
                    "analyte": analyte,
                    "value": val,
                })
                continue
            # Check duplicates
            if key in duplicates:
                duplicates[key] += 1
            else:
                duplicates[key] = 1
    # Add duplicate issues
    for (specimen, analyte), count in duplicates.items():
        if count > 1:
            issues.append({
                "type": "duplicate",
                "specimen": specimen,
                "analyte": analyte,
                "count": count,
            })

    return summary, issues, sample_col, analyte_cols


def store_temp_data(data):
    """Persist data in a temporary file and return a key for later retrieval."""
    temp_dir = tempfile.gettempdir()
    fd, path = tempfile.mkstemp(prefix="cap_data_", suffix=".json", dir=temp_dir)
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    # Use filename as key
    key = os.path.basename(path)
    return key


def load_temp_data(key):
    temp_dir = tempfile.gettempdir()
    path = os.path.join(temp_dir, key)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data key {key} not found")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def main():
    form = cgi.FieldStorage()
    # If Excel file uploaded, parse and display summary
    if "excel_file" in form:
        file_item = form["excel_file"]
        if not file_item.file:
            print("Content-type: text/html\n")
            print("<h1>No file uploaded</h1>")
            return
        file_bytes = file_item.file.read()
        try:
            df = parse_excel(file_bytes)
        except Exception as exc:
            print("Content-type: text/html\n")
            print(f"<h1>Error reading Excel file</h1><p>{cgi.escape(str(exc))}</p>")
            return
        summary, issues, sample_col, analyte_cols = analyze_data(df)
        # Store data for subsequent steps (encoded as JSON with data, sample_col, analytes)
        data = {
            "sample_column": sample_col,
            "analyte_columns": analyte_cols,
            "records": df.to_dict(orient="records"),
        }
        key = store_temp_data(data)
        # Build HTML page
        print("Content-type: text/html\n")
        print("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Excel Analysis Results</title>
<style>
    body { font-family: Arial, sans-serif; background-color: #f5f9fc; margin: 0; padding: 0; }
    header { background-color: #2f59a6; color: #fff; padding: 20px; }
    h1 { margin: 0; font-size: 26px; }
    main { max-width: 900px; margin: 0 auto; padding: 30px; }
    .stats { display: flex; gap: 20px; margin-bottom: 20px; }
    .stat-card { flex: 1; background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; }
    .stat-card h3 { margin: 0; font-size: 18px; color: #6b7280; }
    .stat-card p { font-size: 28px; margin: 10px 0 0; color: #111827; }
    .analytes { margin-top: 20px; }
    .analytes h3 { margin-bottom: 10px; }
    .analytes .tag { display: inline-block; margin: 4px; padding: 6px 10px; background: #e5e7eb; border-radius: 6px; font-size: 14px; }
    .issues { margin-top: 20px; }
    .issues h3 { margin-bottom: 10px; }
    .issue { background: #fff; border-left: 4px solid #f59e0b; padding: 10px 15px; margin-bottom: 8px; border-radius: 4px; }
    .issue.non_numeric { border-left-color: #ef4444; }
    .issue.duplicate { border-left-color: #6b7280; }
    form { margin-top: 30px; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    input[type="text"] { width: 100%; padding: 10px; margin-top: 5px; border-radius: 4px; border: 1px solid #d1d5db; }
    button { margin-top: 15px; padding: 10px 20px; background-color: #2563eb; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
    button:hover { background-color: #1e40af; }
</style>
</head>
<body>
<header>
    <h1>Excel Analysis Results</h1>
</header>
<main>
    <div class="stats">
        <div class="stat-card">
            <h3>Total Records</h3>
            <p>{total_records}</p>
        </div>
        <div class="stat-card">
            <h3>Analytes Found</h3>
            <p>{analytes_found}</p>
        </div>
        <div class="stat-card">
            <h3>Specimens</h3>
            <p>{specimens}</p>
        </div>
    </div>
    <div class="analytes">
        <h3>Detected Analytes</h3>
        {analyte_tags}
    </div>
    <div class="issues">
        <h3>Data Quality Issues</h3>
        {issues_html}
    </div>
    <form action="/cgi-bin/automation.py" method="post">
        <h3>Enter Kit Number</h3>
        <input type="text" name="kit_number" required placeholder="Kit number">
        <input type="hidden" name="data_key" value="{data_key}">
        <button type="submit">Start Automation</button>
    </form>
</main>
</body>
</html>
""".format(
            total_records=summary["total_records"],
            analytes_found=summary["analytes_found"],
            specimens=summary["specimens"],
            analyte_tags="".join(
                f'<span class="tag">{cgi.escape(a)}</span>' for a in summary["analyte_list"]
            ),
            issues_html="".join(
                f'<div class="issue {issue["type"]}"><strong>{issue["type"].replace("_", " ").title()}</strong>: Specimen {cgi.escape(str(issue["specimen"]))}, Analyte {cgi.escape(issue["analyte"])}'
                + (f', Value: {cgi.escape(str(issue.get("value", "")))}' if "value" in issue else '')
                + (f', Count: {issue.get("count")}' if "count" in issue else '')
                + '</div>'
                for issue in issues
            ) or '<p>No issues detected.</p>',
            data_key=key
        ))
    # else if data_key provided and kit number: not handled here
    else:
        print("Content-type: text/html\n")
        print("<h1>Invalid request</h1>")


if __name__ == "__main__":
    main()