#!/bin/bash

# Get the IP address and hostname of the current machine
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)
HOSTNAME=$(hostname)

# Print the IP address and hostname
echo "Your Hostname: $HOSTNAME"
echo "Your IP Address: $IP_ADDRESS"

# Prompt the user to enter the IP or subnet to scan
read -p "Enter the IP or subnet to scan (in CIDR notation): " SUBNET

# Print the subnet to be scanned
echo "Scanning Subnet: $SUBNET"

# Scan the subnet for open RDP ports and attempt to connect
nmap -p 3389 $SUBNET | grep -q "3389/tcp open" && xfreerdp /v:$SUBNET

# Print the current date and time
echo "Script ran at $(date)"
