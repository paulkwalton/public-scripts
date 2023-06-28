#!/bin/bash

# Get the IP address of the current machine
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)

# Get the subnet
SUBNET=$(echo $IP_ADDRESS | cut -d'.' -f1-3)

# Scan the subnet for open Telnet ports and launch Telnet connections
for i in $(seq 1 254); do
    if nmap -p 23 $SUBNET.$i | grep -q "23/tcp open"; then
        gnome-terminal -- telnet $SUBNET.$i &
    fi
done
