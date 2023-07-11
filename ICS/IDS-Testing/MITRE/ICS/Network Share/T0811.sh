#!/bin/bash

# Get the IP address and hostname of the current machine
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)
HOSTNAME=$(hostname)

# Print the IP address and hostname
echo "Your Hostname: $HOSTNAME"
echo "Your IP Address: $IP_ADDRESS"

# Prompt the user to enter the IP or subnet to scan
read -p "Enter the subnet to scan (in CIDR notation): " SUBNET

# Print the subnet to be scanned
echo "Scanning Subnet: $SUBNET for open SMB shares"

# Scan the subnet for open SMB ports and list shares
nmap -p 445 --open -oG - $SUBNET | awk '/Up$/{print $2}' | while read line; do
    echo "Open SMB shares at $line"
    smbclient -N -L \\$line
done

# Print the current date and time
echo "Script ran at $(date)"
