#!/bin/bash

# This script is designed to scan a target system for the MS08-067 vulnerability
# using the ms08_067_netapi module in Metasploit. 

read -p "Enter target IP: " target_ip

# Creating Metasploit rc file
cat > ms08_067_scan.rc <<EOF
use auxiliary/scanner/smb/smb_ms08_067
set RHOSTS $target_ip
run
exit
EOF

# Running Metasploit with the created rc file
msfconsole -r ms08_067_scan.rc

echo "Script ran at $(date)"
