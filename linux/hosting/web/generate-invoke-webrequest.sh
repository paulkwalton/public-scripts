#!/bin/bash

# Prompt the user for a URL
echo "Please enter the URL:"
read url

# Check if the URL is valid
if [[ ! $url =~ ^https?:// ]]; then
    echo "Invalid URL. Please enter a URL starting with 'http://' or 'https://'"
    exit 1
fi

# Generate the PowerShell Invoke-WebRequest command
powershell_command="powershell.exe -Command \"Invoke-WebRequest -Uri '$url'\""

# Print the generated command
echo "Generated PowerShell command:"
echo "$powershell_command"
