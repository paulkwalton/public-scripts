#!/bin/bash

# Function to generate a random MAC address
generate_mac() {
    printf '02:%02x:%02x:%02x:%02x:%02x\n' $[RANDOM%256] $[RANDOM%256] $[RANDOM%256] $[RANDOM%256] $[RANDOM%256]
}

# Get the hostname
hostname=$(hostname)

# Get the IP address
ip_address=$(hostname -I | cut -d' ' -f1)

echo "Hostname: $hostname"
echo "IP: $ip_address"

# Infinite loop to change MAC address every minute
while true; do
    # Generate a random MAC address
    new_mac=$(generate_mac)

    # Disable the network interface
    sudo ifconfig eth0 down

    # Change the MAC address
    sudo ifconfig eth0 hw ether $new_mac

    # Enable the network interface
    sudo ifconfig eth0 up

    # Get the current timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Print out a confirmation message
    echo "[$timestamp] MAC address changed to $new_mac"

    # Sleep for a minute before the next change
    sleep 60
done
