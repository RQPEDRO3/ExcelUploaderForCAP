#!/bin/bash
# Convenience script to launch the CAP Data Entry Automation app on macOS.

# Resolve the directory where this script resides.
DIR="$(cd "$(dirname "$0")" && pwd)"

# Change to that directory.
cd "$DIR" || exit 1

# Start a CGI-enabled HTTP server on port 8080 in the background.
python3 -m http.server --cgi 8080 &
SERVER_PID=$!

# Give the server a moment to start.
sleep 2

# Open the default web browser pointing to the app.
open "http://localhost:8080/"

# Wait for the server process to exit when the user quits the browser.
wait $SERVER_PID