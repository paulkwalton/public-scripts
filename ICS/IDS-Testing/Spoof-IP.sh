#!/bin/bash

# Get the current machine's hostname
HOSTNAME=$(hostname)

# Print the hostname
echo "Your Hostname: $HOSTNAME"

# Prompt the user to enter the subnet to scan
read -p "Enter the subnet to scan (in CIDR notation): " SUBNET

# Perform a ping scan to find responsive hosts
echo "Scanning subnet: $SUBNET..."
HOSTS=$(nmap -sn $SUBNET -oG - | awk '/Up$/{print $2}')

# Display the responsive hosts to the user
echo "Responsive hosts:"
select IP in $HOSTS; do
    if [[ -n $IP ]]; then
        echo "You selected IP: $IP"
        break
    else
        echo "Invalid selection."
    fi
done

# Prompt the user to confirm IP spoofing
read -p "Are you sure you want to spoof this IP? This will change your system's IP address. (yes/no): " CONFIRM
if [[ $CONFIRM == "yes" ]]; then
    # Prompt the user to enter the network interface
    read -p "Enter the network interface to change (e.g. eth0): " INTERFACE
    # Change the IP address of the selected interface
    sudo ip addr flush dev $INTERFACE
    sudo ip addr add $IP/24 dev $INTERFACE
    echo "IP address changed to: $IP"
else
    echo "Operation cancelled."
fi

# Print the current date and time
echo "Script ran at $(date)"
