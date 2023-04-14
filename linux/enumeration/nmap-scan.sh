#!/bin/bash

# Get the IP address of the current machine
function get_local_ip() {
  local local_ip
  local_ip=$(hostname -I | awk '{print $1}')
  echo $local_ip
}

# Function to display a colored and formatted menu
function display_menu() {
  local local_ip=$1
  echo -e "\033[1;32mNmap Scanner\033[0m"
  echo -e "Scanning from IP address: \033[1;31m$local_ip\033[0m"
  echo ""
  echo "Enter the destination IP address to scan:"
  read ip_address
  echo -e "You have entered the destination IP: \033[1;31m$ip_address\033[0m"
  echo ""
  echo -e "\033[1mChoose the type of scan you want to perform:\033[0m"
  echo "1. TCP scan"
  echo "2. UDP scan"
  echo "3. Both TCP and UDP scan"
  echo ""
  echo -n "Enter your choice (1, 2, or 3): "
}

# Script for running nmap with the -A option

local_ip=$(get_local_ip)

display_menu $local_ip

read choice

echo ""

# Save scan output to a temporary file
output_file="/tmp/nmap_scan_output.txt"

case $choice in
  1)
    echo -e "TCP scan initiated on IP: \033[1;31m$ip_address\033[0m"
    nmap -p 1-65535 -A --open $ip_address > $output_file
    ;;
  2)
    echo -e "UDP scan initiated on IP: \033[1;31m$ip_address\033[0m"
    nmap -sU -A --open $ip_address > $output_file
    ;;
  3)
    echo -e "Both TCP and UDP scan initiated on IP: \033[1;31m$ip_address\033[0m"
    nmap -p 1-65535 -sU -A --open $ip_address > $output_file
    ;;
  *)
    echo "Invalid option. Please choose 1, 2, or 3."
    exit 1
    ;;
esac

# Display the scan output
cat $output_file

# Clean up temporary files
rm $output_file
