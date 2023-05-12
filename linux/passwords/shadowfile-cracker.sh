#!/bin/bash

# Path to the wordlist folder
WORDLIST_FOLDER="/usr/share/seclists/Passwords/Common-Credentials/"

# Prompt the user for the shadow file
read -p "Enter the path to the shadow file: " SHADOW_FILE

# Expand the path if tab completion is used
SHADOW_FILE=$(readlink -f "$SHADOW_FILE")

# Check if the shadow file exists
if [ ! -f "$SHADOW_FILE" ]; then
    echo "Shadow file not found."
    exit 1
fi

# Check if the wordlist folder exists
if [ ! -d "$WORDLIST_FOLDER" ]; then
    echo "Wordlist folder not found."
    exit 1
fi

# Get a list of all wordlists in the folder
WORDLISTS=$(find "$WORDLIST_FOLDER" -type f)

# Iterate over each wordlist and crack the hashes
for WORDLIST in $WORDLISTS; do
    echo "Cracking hashes using wordlist: $WORDLIST"
    john --wordlist="$WORDLIST" "$SHADOW_FILE"
done
