#!/bin/bash

# This script is designed to scan a target system for the MS17-010 vulnerability
# (also known as "EternalBlue") using the smb_ms17_010 module in Metasploit. 

read -p "Enter target IP: " target_ip

# Creating Metasploit rc file
cat > ms17_010_scan.rc <<EOF
use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS $target_ip
run
exit
EOF

# Running Metasploit with the created rc file
msfconsole -r ms17_010_scan.rc
