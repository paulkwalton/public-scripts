#!/bin/bash

# Check if the user has provided an IP range as an argument
if [ -z "$1" ]; then
  echo "Usage: ./snmp_scan.sh <IP-range>"
  exit 1
fi

# Define the IP range
ip_range=$1

# Create a list of common SNMP community strings
echo "public" > community_strings.txt
echo "private" >> community_strings.txt
echo "manager" >> community_strings.txt
echo "cisco" >> community_strings.txt
echo "admin" >> community_strings.txt

# Scan the IP range for exposed SNMPv1 and 2 using onesixtyone
onesixtyone -c community_strings.txt -o snmp_results.txt $ip_range

# Display the results and save them to a file
echo "SNMP scan results:"
cat snmp_results.txt

# Retrieve OID data using snmpwalk
while read -r line; do
  ip=$(echo $line | awk '{print $1}')
  community=$(echo $line | awk '{print $2}')
  community=${community//\[/} # Remove brackets from the community string
  community=${community//\]/}
  echo "Retrieving OID data for $ip using community string $community"
  snmpwalk -v 2c -c $community $ip $base_oid 
 
done < snmp_results.txt

# Cleanup
rm community_strings.txt
