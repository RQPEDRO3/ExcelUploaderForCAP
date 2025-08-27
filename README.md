# CAP Data Entry Automation

This repository contains a prototype web application for automating data entry into the College of American Pathologists (CAP) e‑LAB Solutions Suite.  It allows you to upload Excel files containing specimen IDs and analyte values, performs basic quality checks, and provides a foundation for automating result form submission to CAP.

## Features

* **Upload and parse Excel files**: Automatically detects specimen/sample ID columns and analyte value columns (ignoring unit/qualifier/unnamed columns).
* **Data summary**: Displays total record count, number of analytes found, number of unique specimens, and lists detected analytes.
* **Quality checks**: Flags missing values, non‑numeric values, and duplicate specimen–analyte combinations.
* **Kit number entry**: Prompts for a kit number as a placeholder for future automation.

## Requirements

* Python 3.8 or newer
* The `pandas` library (`pip install pandas`)
* A modern web browser

In a complete solution, additional dependencies such as Flask and Playwright would be needed to implement the full automation flow.  Those are not included in this prototype.

## Running the prototype

### Using the `start.command` script (macOS)

On macOS you can avoid typing Terminal commands by using the provided `start.command` file:

1. Download or clone this repository.
2. Open Finder and navigate to the `cap_app` folder.
3. Double‑click `start.command`.  This will launch a local CGI‑enabled HTTP server on port 8080 and automatically open the app in your default browser.
4. Use the **Open Excel File** button on the home page to upload your Excel file and begin the workflow.

### Using the Terminal

If you prefer or are on a different platform (e.g. Linux):

```bash
cd path/to/cap_app
python3 -m http.server --cgi 8080
```

Then open `http://localhost:8080/` in your browser.

## Notes

This project uses Python’s built‑in `http.server` and `cgi` modules to avoid external dependencies.  It provides a starting point for the CAP automation workflow but does not implement the Playwright‑based submission process.  Contributions are welcome!