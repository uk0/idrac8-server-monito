#!/bin/bash

echo "Starting IDRAC8 Monitor Backend Service..."

# Navigate to backend directory
cd backend

# Download dependencies
go mod tidy

# Build the application
echo "Building Go application..."
go build -o idrac-monitor main.go

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build successful. Starting server..."
    # Run the application
    ./idrac-monitor
else
    echo "Build failed. Please check the code for errors."
    exit 1
fi