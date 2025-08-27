# Add these imports at the top of your upload.py file
from cap_automation import perform_cap_automation, AutomationConfig

# Replace the generate_success_page function with this updated version
def generate_success_page(kit_number, summary, issues, data_key, automation_result=None):
    """Generate the success page with analysis results and automation status."""
    # Generate analyte tags
    analyte_tags = "".join(
        f'<span class="tag">{html.escape(str(a))}</span>' for a in summary["analyte_list"]
    )
    
    # Generate issues HTML
    if issues:
        issues_html = ""
        for issue in issues:
            issue_class = issue["type"]
            issue_title = issue["type"].replace("_", " ").title()
            
            if issue["type"] == "error":
                issues_html += f'<div class="issue error"><strong>Error</strong>: {html.escape(issue["message"])}</div>'
            else:
                specimen = html.escape(str(issue.get("specimen", "N/A")))
                analyte = html.escape(str(issue.get("analyte", "N/A")))
                
                issues_html += f'<div class="issue {issue_class}"><strong>{issue_title}</strong>: Specimen {specimen}, Analyte {analyte}'
                
                if "value" in issue:
                    value = html.escape(str(issue["value"]))
                    issues_html += f', Value: {value}'
                
                if "count" in issue:
                    issues_html += f', Count: {issue["count"]}'
                
                issues_html += '</div>'
    else:
        issues_html = '<div class="no-issues">No issues detected.</div>'
    
    # Generate automation status HTML
    if automation_result:
        success, message = automation_result
        if success:
            automation_html = f'''
            <div class="automation-status success">
                <h4>✅ Automation Completed Successfully</h4>
                <p><strong>Status:</strong> Data successfully submitted to CAP portal</p>
                <p><strong>Kit Number:</strong> {html.escape(kit_number)}</p>
                <p><strong>Result:</strong> {html.escape(message)}</p>
            </div>'''
            automation_class = "success-banner"
            banner_text = f"✅ Excel file processed and data submitted to CAP portal for Kit {html.escape(kit_number)}"
        else:
            automation_html = f'''
            <div class="automation-status error">
                <h4>❌ Automation Failed</h4>
                <p><strong>Status:</strong> Could not submit data to CAP portal</p>
                <p><strong>Kit Number:</strong> {html.escape(kit_number)}</p>
                <p><strong>Error:</strong> {html.escape(message)}</p>
                <p><em>Please check your configuration and try again, or submit data manually.</em></p>
            </div>'''
            automation_class = "error-banner"
            banner_text = f"⚠️ Excel file processed but automation failed for Kit {html.escape(kit_number)}"
    else:
        automation_html = '''
        <div class="automation-status">
            <h4>Automation Status</h4>
            <p><strong>Status:</strong> Ready for CAP portal integration</p>
            <p><strong>Next Steps:</strong> Configure automation settings to enable automatic data submission.</p>
        </div>'''
        automation_class = "success-banner"
        banner_text = f"✓ Excel file processed for Kit {html.escape(kit_number)}"
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Processing Complete - Kit {html.escape(kit_number)}</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif;
            background-color: #f5f9fc; 
            margin: 0; 
            padding: 0; 
            line-height: 1.6;
        }}
        header {{ 
            background-color: #2f59a6; 
            color: #fff; 
            padding: 20px; 
        }}
        h1 {{ 
            margin: 0; 
            font-size: 26px; 
            font-weight: bold;
        }}
        main {{ 
            max-width: 900px; 
            margin: 0 auto; 
            padding: 30px 20px; 
        }}
        .success-banner {{ 
            background: #10b981; 
            color: white; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 30px; 
            text-align: center; 
            font-size: 18px; 
            font-weight: bold;
        }}
        .error-banner {{ 
            background: #ef4444; 
            color: white; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 30px; 
            text-align: center; 
            font-size: 18px; 
            font-weight: bold;
        }}
        .stats {{ 
            display: flex; 
            gap: 20px; 
            margin-bottom: 30px; 
            flex-wrap: wrap; 
        }}
        .stat-card {{ 
            flex: 1; 
            min-width: 200px; 
            background: #fff; 
            border-radius: 8px; 
            padding: 20px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
            text-align: center; 
        }}
        .stat-card h3 {{ 
            margin: 0; 
            font-size: 18px; 
            color: #6b7280; 
            font-weight: bold;
        }}
        .stat-card p {{ 
            font-size: 28px; 
            margin: 10px 0 0; 
            color: #111827; 
            font-weight: bold; 
        }}
        .section {{ 
            background: #fff; 
            border-radius: 8px; 
            padding: 25px; 
            margin-bottom: 20px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
        }}
        .section h3 {{ 
            margin-top: 0; 
            color: #374151; 
            font-weight: bold;
        }}
        .tag {{ 
            display: inline-block; 
            margin: 4px; 
            padding: 6px 10px; 
            background: #e5e7eb; 
            border-radius: 6px; 
            font-size: 14px; 
            font-weight: bold;
        }}
        .issue {{ 
            background: #fff; 
            border-left: 4px solid #f59e0b; 
            padding: 10px 15px; 
            margin-bottom: 8px; 
            border-radius: 4px; 
            font-size: 14px;
        }}
        .issue.non_numeric {{ 
            border-left-color: #ef4444; 
        }}
        .issue.duplicate {{ 
            border-left-color: #6b7280; 
        }}
        .issue.error {{ 
            border-left-color: #dc2626; 
            background: #fef2f2; 
        }}
        .no-issues {{ 
            color: #10b981; 
            font-style: italic; 
            font-weight: bold;
        }}
        .automation-status {{ 
            background: #eff6ff; 
            border: 1px solid #dbeafe; 
            padding: 20px; 
            border-radius: 8px; 
            margin-top: 20px; 
        }}
        .automation-status.success {{ 
            background: #f0f9f0; 
            border-color: #10b981; 
        }}
        .automation-status.error {{ 
            background: #fef2f2; 
            border-color: #ef4444; 
        }}
        .automation-status h4 {{ 
            margin-top: 0; 
            color: #1e40af; 
            font-weight: bold;
        }}
        .automation-status.success h4 {{ 
            color: #10b981; 
        }}
        .automation-status.error h4 {{ 
            color: #ef4444; 
        }}
        .btn {{ 
            display: inline-block; 
            padding: 12px 24px; 
            background-color: #2563eb; 
            color: #fff; 
            border-radius: 4px; 
            text-decoration: none; 
            margin-top: 20px; 
            margin-right: 10px; 
            font-family: Arial, sans-serif; 
            font-weight: bold;
        }}
        .btn:hover {{ 
            background-color: #1e40af; 
        }}
        .btn-secondary {{ 
            background-color: #6b7280; 
        }}
        .btn-secondary:hover {{ 
            background-color: #4b5563; 
        }}
    </style>
</head>
<body>
<header>
    <h1>Processing Complete</h1>
    <p>Kit Number: {html.escape(kit_number)}</p>
</header>
<main>
    <div class="{automation_class}">
        {banner_text}
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>Total Records</h3>
            <p>{summary['total_records']}</p>
        </div>
        <div class="stat-card">
            <h3>Analytes Found</h3>
            <p>{summary['analytes_found']}</p>
        </div>
        <div class="stat-card">
            <h3>Specimens</h3>
            <p>{summary['specimens']}</p>
        </div>
    </div>
    
    <div class="section">
        <h3>Detected Analytes</h3>
        {analyte_tags if analyte_tags else '<p>No analytes detected</p>'}
    </div>
    
    <div class="section">
        <h3>Data Quality Issues</h3>
        {issues_html}
    </div>
    
    {automation_html}
    
    <a class="btn" href="">Upload Another File</a>
    <a class="btn btn-secondary" href="/">Return to Home</a>
</main>
</body>
</html>"""


# Update the main() function to include automation
def main():
    """Main CGI handler function with automation."""
    try:
        form = cgi.FieldStorage()
        
        # Check if both Excel file and kit number are provided
        if "excel_file" in form and "kit_number" in form:
            kit_number = form.getfirst("kit_number", "").strip()
            file_item = form["excel_file"]
            
            # Validate kit number
            if not kit_number or len(kit_number) < 1:
                print("Content-type: text/html\n")
                print("<h1>Error</h1><p>Kit number is required.</p>")
                return
            
            # Validate file
            if not file_item.file or not file_item.filename:
                print("Content-type: text/html\n")
                print("<h1>Error</h1><p>No file uploaded or invalid file.</p>")
                return
            
            # Read file content
            file_bytes = file_item.file.read()
            
            if not file_bytes:
                print("Content-type: text/html\n")
                print("<h1>Error</h1><p>Uploaded file is empty.</p>")
                return
            
            try:
                df = parse_excel(file_bytes)
            except Exception as exc:
                print("Content-type: text/html\n")
                print(f"<h1>Error reading Excel file</h1><p>{html.escape(str(exc))}</p>")
                return
            
            # Analyze the data
            summary, issues, sample_col, analyte_cols = analyze_data(df)
            
            # Store data for automation
            data = {
                "kit_number": kit_number,
                "sample_column": sample_col,
                "analyte_columns": analyte_cols,
                "records": df.to_dict(orient="records"),
                "summary": summary
            }
            
            try:
                data_key = store_temp_data(data)
            except Exception as exc:
                print("Content-type: text/html\n")
                print(f"<h1>Error storing data</h1><p>{html.escape(str(exc))}</p>")
                return
            
            # Attempt automation
            automation_result = None
            try:
                # Check if automation is configured
                config_manager = AutomationConfig()
                if config_manager.is_configured():
                    automation_result = perform_cap_automation(kit_number, data)
                else:
                    automation_result = (False, "Automation not configured. Please set up CAP portal credentials.")
            except Exception as e:
                automation_result = (False, f"Automation error: {str(e)}")
            
            # Generate and send success page
            print("Content-type: text/html\n")
            print(generate_success_page(kit_number, summary, issues, data_key, automation_result))
            
        else:
            # Show upload form
            print("Content-type: text/html\n")
            print(generate_upload_form())
    
    except Exception as e:
        # Handle any unexpected errors
        print("Content-type: text/html\n")
        print(f"<h1>Unexpected Error</h1><p>An error occurred: {html.escape(str(e))}</p>")
!/usr/bin/env python3
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
import html
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
            # Escape error message using html.escape instead of the removed cgi.escape
            print(f"<h1>Error reading Excel file</h1><p>{html.escape(str(exc))}</p>")
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
                f'<span class="tag">{html.escape(a)}</span>' for a in summary["analyte_list"]
            ),
            issues_html="".join(
                f'<div class="issue {issue["type"]}"><strong>{issue["type"].replace("_", " ").title()}</strong>: Specimen {html.escape(str(issue["specimen"]))}, Analyte {html.escape(issue["analyte"])}'
                + (f', Value: {html.escape(str(issue.get("value", "")))}' if "value" in issue else '')
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
