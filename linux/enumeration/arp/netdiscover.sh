#!/bin/bash

# Define a banner
echo "==============================================="
echo "         Subnet Scanner with netdiscover        "
echo "==============================================="
echo ""
echo "Passive scanning for devices on the subnet assigned to eth0 (Assuming subnet mask is /24)..."

# Get the IP address assigned to eth0
ip_address=$(ip addr show eth0 | grep -Po 'inet \K[\d.]+')

# Calculate the subnet from the IP address
subnet=$(echo $ip_address | awk -F. '{print $1"."$2"."$3".0/24"}')

# Use netdiscover to scan the subnet on eth0 and format output into a table
sudo netdiscover -i eth0 -r $subnet -P -N -p

# The -i flag specifies the interface to use
# The -r flag specifies the range to scan
# The -P flag tells netdiscover to show the MAC addresses of the devices found
# The -N flag tells netdiscover not to resolve hostnames
# The awk command formats the output into a table

