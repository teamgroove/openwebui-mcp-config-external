#!/bin/bash
set -e

# Install dependencies from mcp-sharepoint if requirements.txt exists
if [ -f /app/mcp-sharepoint/requirements.txt ]; then
    echo "Installing SharePoint MCP dependencies..."
    pip install -r /app/mcp-sharepoint/requirements.txt
fi

# Function to handle process termination
cleanup() {
    echo "Received termination signal. Shutting down..."
    if [ -n "$SHAREPOINT_PID" ] && ps -p $SHAREPOINT_PID > /dev/null; then
        kill $SHAREPOINT_PID
    fi
    if [ -n "$MCPO_PID" ] && ps -p $MCPO_PID > /dev/null; then
        kill $MCPO_PID
    fi
    exit 0
}

# Set up signal handling
trap cleanup SIGTERM SIGINT

# Start the SharePoint MCP server in the background
echo "Starting SharePoint MCP server..."
cd /app/mcp-sharepoint
python -m uvicorn main:app --host 0.0.0.0 --port 8001 &
SHAREPOINT_PID=$!
echo "SharePoint MCP server started with PID: $SHAREPOINT_PID"

# Wait a moment to ensure SharePoint MCP server starts
sleep 5

# Start the MCPO server
echo "Starting MCPO server..."
cd /app
python -m mcpo.main "$@" &
MCPO_PID=$!
echo "MCPO server started with PID: $MCPO_PID"

# Keep the script running
echo "Both servers started. Waiting for processes..."
wait $SHAREPOINT_PID $MCPO_PID
