#!/bin/bash

# Prompt the user for their username, target host, and file to upload
read -p "Enter your username: " user
read -p "Enter the target host: " target_host
echo "Enter the file location (use TAB for auto-completion): "
read -e file_to_upload

# Upload the file to the target host's /opt/ directory
scp "$file_to_upload" "$user"@"$target_host":/opt/

# Check if the file was uploaded successfully
if [ $? -eq 0 ]; then
    echo "File uploaded successfully to $target_host:/tmp/"
else
    echo "File upload failed. Please check your details and try again."
fi
