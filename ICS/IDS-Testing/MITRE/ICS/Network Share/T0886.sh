#!/bin/bash

# Prompt the user to enter the file path to upload
read -p "Enter the file path to upload: " FILE_PATH

# Prompt for the SMB share details
read -p "Enter the remote SMB server IP: " SMB_SERVER
read -p "Enter the remote SMB share name: " SMB_SHARE

# Check if the file exists and upload it
if [ -f "$FILE_PATH" ]; then
    echo "Uploading file: $FILE_PATH"
    smbclient //$SMB_SERVER/$SMB_SHARE -N -c "put $FILE_PATH"
else
    echo "File does not exist: $FILE_PATH"
fi

# Print the current date and time
echo "Script ran at $(date)"

