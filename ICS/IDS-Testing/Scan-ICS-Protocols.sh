#!/bin/bash

# Get the IP address and hostname of the current machine
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)
HOSTNAME=$(hostname)

# Print the IP address and hostname
echo "Your Hostname: $HOSTNAME"
echo "Your IP Address: $IP_ADDRESS"

# Prompt the user to enter the IP or subnet to scan
read -p "Enter the subnet to scan (in CIDR notation): " SUBNET

# Define a string with common ICS port numbers including Ethernet/IP
ICS_PORTS="102,502,20000,44818,2222"

# Description of the ports being scanned
echo "Scanning Subnet: $SUBNET for common ICS ports:"
echo " - IEC 61850 (port 102)"
echo " - Modbus (port 502)"
echo " - DNP3 (port 20000)"
echo " - Ethernet/IP over TCP (port 44818)"
echo " - Ethernet/IP over UDP (port 2222)"

# Scan the subnet for open ICS ports
nmap -p $ICS_PORTS --open -oG - $SUBNET | awk '/Up$/{print $2}' | while read line; do
    echo "Host with open ICS ports: $line"
done

# Print the current date and time
echo "Script ran at $(date)"
