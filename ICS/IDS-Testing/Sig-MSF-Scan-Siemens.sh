Certainly, if you are testing your own environment or have explicit permission to test, you could automate Metasploit's `auxiliary/scanner/scada/profinet_siemens` module with a script. Here's how to do it:

```bash
#!/bin/bash

read -p "Enter target IP range (in CIDR notation): " target_ip_range

cat > profinet_scan.rc <<EOF
use auxiliary/scanner/scada/profinet_siemens
set RHOSTS $target_ip_range
run
exit
EOF

msfconsole -r profinet_scan.rc
```

This script prompts for the target IP range, creates a Metasploit resource script with these details, and then executes the `msfconsole` command with the resource script.

As always, please ensure that you have the proper authorization to perform these scans. Scanning systems without explicit permission is illegal and unethical.
