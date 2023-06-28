#!/bin/bash

# Get the IP address of the current machine
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)

# Get the hostname
HOSTNAME=$(hostname)

# Print the hostname and IP address
echo "Running on host: $HOSTNAME"
echo "IP Address: $IP_ADDRESS"

# Get the subnet
SUBNET=$(echo $IP_ADDRESS | cut -d'.' -f1-3)

# Perform a ping sweep of the subnet
for i in $(seq 1 254); do
    if nmap -sn $SUBNET.$i | grep -q "Host is up"; then
        echo "$SUBNET.$i is up"
    fi
done

# Print the current date and time
echo "Script ran at $(date)"
