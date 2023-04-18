#!/bin/bash

# Exit the script with a warning message if running as root
if [ "$(id -u)" -eq 0 ]; then
    echo "WARNING: Do not run this script as root. Exiting."
    exit 1
fi

# Prompt the user to enter the network subnet
echo "Please enter the network subnet (e.g., 192.168.1.0/24):"
read subnet

# Define the output file for Nmap results
nmap_output="nmap_results.txt"

# Run Nmap to enumerate webservers on the network using the provided subnet
nmap -sT -Pn $subnet -p 80,443,8080,8443 --open -oG $nmap_output

# Extract IP addresses from the Nmap output
ip_addresses=$(cat $nmap_output | grep "Ports:" | cut -d" " -f2)

# Save IP addresses to a text file
ip_list="ip_list.txt"
echo "$ip_addresses" > $ip_list

# Run Eyewitness on the list of IP addresses
eyewitness -f $ip_list --web
