#!/bin/bash

# Start the backend server
echo "Starting AI Trust Backend..."
./venv/bin/python backend/main.py &

# Wait for backend to start
sleep 2

# Open the dashboard in the browser
echo "Opening Dashboard..."
# Since I can't open a real browser on the user's screen easily, 
# I'll just print the instructions.

echo "System is LIVE!"
echo "Backend: http://localhost:8000"
echo "Dashboard: Open /home/error/Documents/val/frontend/index.html in your browser"
echo "Extension: Load the '/extension' folder into Chrome (Developer Mode)"
