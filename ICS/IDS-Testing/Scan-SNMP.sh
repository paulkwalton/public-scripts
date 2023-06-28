#!/bin/bash

# Retrieve Hostname and IP
HOSTNAME=$(hostname)
IP=$(hostname -I | awk '{print $1}')

# Check if the user has provided an IP range as an argument
if [ -z "$1" ]; then
  echo "Usage: ./snmp_scan.sh <IP-range>"
  exit 1
fi

# Define the IP range
ip_range=$1

# Create a list of common SNMP community strings
community_strings=(
public private 0 0392a0 1234 2read 4changes ANYCOM Admin C0de CISCO CR52401
IBM ILMI Intermec NoGaH\$@! OrigEquipMfr PRIVATE PUBLIC Private Public SECRET
SECURITY SNMP SNMP_trap SUN SWITCH SYSTEM Secret Security Switch System
TENmanUFactOryPOWER TEST access adm admin agent agent_steal all all private
all public apc bintec blue c cable-d canon_admin cc cisco community core
debug default dilbert enable field field-service freekevin fubar guest hello
hp_admin ibm ilmi intermec internal l2 l3 manager mngt monitor netman network
none openview pass password pr1v4t3 proxy publ1c read read-only read-write
readwrite red regional rmon rmon_admin ro root router rw rwa san-fran sanfran
scotty secret security seri snmp snmpd snmptrap solaris sun superuser switch
system tech test test2 tiv0li tivoli trap world write xyzzy yellow
)

printf "%s\n" "${community_strings[@]}" > community_strings.txt

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

# Print timestamp, hostname, and IP at the end
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "Script ran at $TIMESTAMP"
echo "Hostname: $HOSTNAME"
echo "IP: $IP"
