#!/bin/bash

# Prompt the user to enter the IP or subnet to scan
read -p "Enter the IP or subnet to scan (in CIDR notation): " SUBNET

# Get the IP address and hostname of the current machine
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)
HOSTNAME=$(hostname)

# Print the IP address, hostname, and subnet
echo "Your Hostname: $HOSTNAME"
echo "Your IP Address: $IP_ADDRESS"
echo "Scanning Subnet: $SUBNET"

# Perform a ping sweep of the subnet
nmap -sn -n -v $SUBNET

# Print the current date and time
echo "Script ran at $(date)"
