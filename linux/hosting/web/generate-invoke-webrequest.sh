#!/bin/bash

# Prompt the user for a URL
echo "Please enter the URL:"
read url

# Check if the URL is valid
if [[ ! $url =~ ^http:// ]]; then
    echo "Invalid URL. Please enter a URL starting with 'http://'"
    exit 1
fi

# Generate the PowerShell 2.0 command using System.Net.WebClient
powershell_2_command="powershell.exe -Command \"\$wc = New-Object System.Net.WebClient; \$wc.DownloadFile('$url', [System.IO.Path]::GetFileName('$url'))\""

# Generate the PowerShell 5.0 command using Invoke-WebRequest
powershell_5_command="powershell.exe -Command \"Invoke-WebRequest -Uri '$url' -OutFile ([System.IO.Path]::GetFileName('$url'))\""

# Print the generated commands
echo "Generated PowerShell commands:"
echo ""
echo "For PowerShell 2.0:"
echo "$powershell_2_command"
echo ""
echo "For PowerShell 5.0 or later:"
echo "$powershell_5_command"
