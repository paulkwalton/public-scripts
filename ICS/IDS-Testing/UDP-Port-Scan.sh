#!/bin/bash

# Get the IP address of the current machine
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)

# Get the subnet
SUBNET=$(echo $IP_ADDRESS | cut -d'.' -f1-3)

# Scan the subnet
for i in $(seq 1 254); do
    nmap -sU $SUBNET.$i
done
