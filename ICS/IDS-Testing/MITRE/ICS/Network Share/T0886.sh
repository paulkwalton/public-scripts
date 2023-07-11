#!/bin/bash

# This script is designed to upload a file to a remote SMB share.
# It first prompts the user for the path to a local file to upload.
# Then it prompts the user for the IP address of the remote SMB server
# and the name of the SMB share on that server.
# If the local file exists, it uses the smbclient utility to upload the file
# to the specified SMB share. If the local file does not exist, it outputs an error message.
# It ends by printing the current date and time, which can be useful for logging purposes.

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


