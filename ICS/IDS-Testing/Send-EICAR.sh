#!/bin/bash

# Get the IP address and hostname of the current machine
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)
HOSTNAME=$(hostname)

# Print the IP address and hostname
echo "Your Hostname: $HOSTNAME"
echo "Your IP Address: $IP_ADDRESS"

# Prompt the user to enter the target IP and TCP port
read -p "Enter the target IP to send the EICAR test file: " TARGET_IP
read -p "Enter the TCP port to use: " TARGET_PORT

# Generate the EICAR test file
echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > eicar_test.txt

# Use netcat to send the file to the target IP on the specified port
nc $TARGET_IP $TARGET_PORT < eicar_test.txt

# Print the current date and time
echo "Script ran at $(date)"
