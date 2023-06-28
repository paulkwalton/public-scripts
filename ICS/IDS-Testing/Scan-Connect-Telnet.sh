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
echo "Scanning Subnet: $SUBNET"

# Scan the subnet for open Telnet ports and attempt to connect to each open port
nmap -p 23 --open -oG - $SUBNET | awk '/Up$/{print $2}' | while read line; do
    echo "Attempting to connect to $line via Telnet"
    expect -c "
    spawn telnet $line
    expect \"login:\"
    send \"fakeuser\r\"
    expect \"Password:\"
    send \"fakepassword\r\"
    expect eof
    "
done

# Print the current date and time
echo "Script ran at $(date)"

