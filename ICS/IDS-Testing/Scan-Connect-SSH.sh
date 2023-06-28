#!/bin/bash

# Get the IP address of the current machine
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)

# Get the subnet
SUBNET=$(echo $IP_ADDRESS | cut -d'.' -f1-3)

# Scan the subnet for open SSH ports and attempt to connect
for i in $(seq 1 254); do
    if nmap -p 22 $SUBNET.$i | grep -q "22/tcp open"; then
        gnome-terminal -- ssh $SUBNET.$i &
    fi
done
