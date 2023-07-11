#!/bin/bash

# This script is designed to discover and list all devices on the network
# that are broadcasting LLDP (Link Layer Discovery Protocol) packets.
# It assumes that the lldpd and lldpcli utilities are installed and available.

# Ensure that lldpd is running
sudo systemctl start lldpd

# Wait a bit for lldpd to collect LLDP information
echo "Waiting for LLDP information collection..."
sleep 10

# Use lldpcli to display the LLDP neighbors
echo "Enumerating LLDP neighbors..."
lldpcli show neighbors

# Print the current date and time
echo "Script ran at $(date)"
