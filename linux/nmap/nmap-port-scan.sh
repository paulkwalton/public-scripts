#!/bin/bash

# Request IP address or network range from the user
echo "Enter an IP address or network range (e.g., 192.168.0.1 or 192.168.0.1/24):"
read target

# Prompt the user for the desired port scan type
echo "Choose the type of port scan:"
echo "1. Full scan (1-65535)"
echo "2. Default port scan"
read scan_choice

# Set the port range based on the user's choice
case $scan_choice in
  1)
    ports="1-65535"
    ;;
  2)
    ports=""
    ;;
  *)
    echo "Invalid choice. Exiting."
    exit 1
    ;;
esac

# Prompt the user for the desired protocol
echo "Choose the protocol(s) to scan:"
echo "1. TCP"
echo "2. UDP"
echo "3. Both"
read protocol_choice

# Set the protocol option and scan type based on the user's choice
case $protocol_choice in
  1)
    scan_type="-sS"
    ;;
  2)
    scan_type="-sU"
    ;;
  3)
    scan_type="-sS -sU"
    ;;
  *)
    echo "Invalid choice. Exiting."
    exit 1
    ;;
esac

# Display the scan settings to the user
echo "Scanning the target with the following settings:"
echo "Target: $target"
echo "Port range: ${ports:-Default}"
echo "Protocol(s): ${scan_type//'-s'/' '} (${scan_type//-s})"
echo "Host discovery: Disabled (-Pn)"
echo "DNS resolution: Disabled (-n)"
echo "Scan speed: T3"

# Perform the Nmap scan with the specified options and safe scripts
if [ -z "$ports" ]; then
  nmap --disable-arp-ping -n -Pn -T3 $scan_type -A -O -v "$target"
else
  nmap --disable-arp-ping -n -Pn -T3 $scan_type -A -O -v -p "$ports" "$target"
fi
