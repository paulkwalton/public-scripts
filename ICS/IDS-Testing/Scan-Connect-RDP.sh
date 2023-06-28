#!/bin/bash

# Get the IP address of the current machine
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)

# Get the subnet
SUBNET=$(echo $IP_ADDRESS | cut -d'.' -f1-3)

# Scan the subnet for open RDP ports and launch RDP connections
for i in $(seq 1 254); do
    if nmap -p 3389 $SUBNET.$i | grep -q "3389/tcp open"; then
        rdesktop $SUBNET.$i &
    fi
done
