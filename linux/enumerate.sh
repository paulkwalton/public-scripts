#!/bin/bash
# Enumeration script for penetration testing
# Usage: ./enumeration_script.sh TARGET_IP

TARGET_IP="$1"

if [ -z "$TARGET_IP" ]; then
  echo "Usage: $0 TARGET_IP"
  exit 1
fi

echo "Target IP: $TARGET_IP"

# Prompt to enable or disable brute force attacks
read -p "Enable brute force attacks? (y/N): " ENABLE_BRUTE_FORCE
if [ "$ENABLE_BRUTE_FORCE" == "y" ] || [ "$ENABLE_BRUTE_FORCE" == "Y" ]; then
  ENABLE_BRUTE_FORCE=true
else
  ENABLE_BRUTE_FORCE=false
fi

# Port scanning and enumeration
echo "Scanning all TCP and default UDP ports on the target..."
TCP_PORTS=$(nmap -p1-65535 -T4 -n "$TARGET_IP" | grep -oP '\d{1,5}/tcp' | cut -d '/' -f1)
UDP_PORTS=$(nmap -sU -T4 -n "$TARGET_IP" | grep -oP '\d{1,5}/udp' | cut -d '/' -f1)

echo "Discovered TCP ports: $TCP_PORTS"
echo "Discovered UDP ports: $UDP_PORTS"

# Enumerate each port with Kali tools
for port in $TCP_PORTS; do
  echo "Enumerating TCP port $port..."

  case $port in
    21)
      # FTP
      echo "FTP detected. Enumerating..."
      nmap -p$port --script ftp-anon,ftp-syst,ftp-proftpd-backdoor -n "$TARGET_IP"
      
      if $ENABLE_BRUTE_FORCE; then
        echo "Brute forcing FTP..."
        hydra -t 4 -l admin -P /usr/share/wordlists/top100.txt -f -v -e nsr -s $port "$TARGET_IP" ftp
      fi

      # Check for anonymous login and download files
      echo "Checking for anonymous FTP login and downloading files..."
      wget -r -nH --no-check-certificate --user=anonymous --password=anonymous "ftp://$TARGET_IP:$port/"
      ;;
    22)
      # SSH
      echo "SSH detected. Enumerating..."
      nmap -p$port --script ssh2-enum-algos,sshv1 -n "$TARGET_IP"
      
      if $ENABLE_BRUTE_FORCE; then
        echo "Brute forcing SSH..."
        hydra -t 4 -L /usr/share/wordlists/top100.txt -P /usr/share/wordlists/top100.txt -f -v -e nsr -s $port "$TARGET_IP" ssh
      fi
      ;;
    23)
      # Telnet
      echo "Telnet detected. Enumerating..."
      nmap -p$port --script telnet-ntlm-info -n "$TARGET_IP"
      
      if $ENABLE_BRUTE_FORCE; then
        echo "Brute forcing Telnet..."
        hydra -t 4 -L /usr/share/wordlists/top100.txt -P /usr/share/wordlists/top100.txt -f -v -e nsr -s $port "$TARGET_IP" telnet
      fi
      ;;
    25)
      # SMTP
      echo "SMTP detected. Enumerating..."
      nmap -p$port --script smtp-commands,smtp-enum-users,smtp-vuln-cve2010-4344,smtp-vuln-cve2011-1720,smtp-vuln-c44,smtp-vuln-cve2011-1764 -n "$TARGET_IP"
      ;;
    53)
      # DNS
      echo "DNS detected. Enumerating..."
      nmap -p$port --script dns-nsid,dns-recursion,dns-service-discovery -n "$TARGET_IP"
      ;;
    80)
      # HTTP
      echo "HTTP detected. Enumerating..."
      nmap -p$port --script http-enum,http-title,http-methods,http-headers -n "$TARGET_IP"
      nikto -h "$TARGET_IP" -p $port
      dirb "http://$TARGET_IP:$port/"
      if $ENABLE_WPS; then
        wpscan --url "http://$TARGET_IP:$port/"
      fi
      ;;
    110)
      # POP3
      echo "POP3 detected. Enumerating..."
      nmap -p$port --script pop3-capabilities,pop3-ntlm-info -n "$TARGET_IP"
      ;;
    139|445)
      # SMB
      echo "SMB detected. Enumerating..."
      nmap -p$port --script smb-enum-shares,smb-vuln-* -n "$TARGET_IP"
      enum4linux -a "$TARGET_IP"
      crackmapexec smb "$TARGET_IP" -u '' -p '' --shares

      # Download files if authentication is not required
      echo "Checking for SMB shares with no credentials required and downloading files..."
      smbclient -N -L "$TARGET_IP" | grep "Disk" | awk '{print $1}' | while read -r share; do
        echo "Attempting to download files from SMB share: $share"
        smbclient -N -c "prompt; recurse; mget *" "//$TARGET_IP/$share"
      done
      ;;
    143)
      # IMAP
      echo "IMAP detected. Enumerating..."
      nmap -p$port --script imap-capabilities,imap-ntlm-info -n "$TARGET_IP"
      ;;
    161)
      # SNMP
      echo "SNMP detected. Enumerating..."
      nmap -p$port --script snmp-brute,snmp-hh3c-logins,snmp-info,snmp-netstat,snmp-processes,snmp-sysdescr,snmp-win32-services,snmp-win32-shares -n "$TARGET_IP"
      ;;
    389|636)
      # LDAP
      echo "LDAP detected. Enumerating..."
      nmap -p$port --script ldap-search,ldap-rootdse -n "$TARGET_IP"
      # Enumerate LDAP users
      BASE_DN=$(ldapsearch -x -h "$TARGET_IP" -p $port -s base -b "" | grep -i 'defaultNamingContext:' | awk '{print $2}')
      echo "Using Base DN: $BASE_DN"
      
      ldapsearch -x -h "$TARGET_IP" -p $port -b "$BASE_DN" "(objectclass=person)" | grep -i "uid:" | awk '{print $2}' > ldap_users.txt
      echo "LDAP users enumerated: $(cat ldap_users.txt)"
      
      if $ENABLE_BRUTE_FORCE; then
        echo "Brute forcing SMB with LDAP enumerated users..."
        crackmapexec smb "$TARGET_IP" -u ldap_users.txt -p /usr/share/wordlists/top100.txt
      fi
      ;;
    443)
      # HTTPS
      echo "HTTPS detected. Enumerating..."
      nmap -p$port --script ssl-enum-ciphers,ssl-cert,ssl-dh-params -n "$TARGET_IP"
      nikto -h "$TARGET_IP" -p $port
      dirb "https://$TARGET_IP:$port/"
      if $ENABLE_WPS; then
        wpscan --url "https://$TARGET_IP:$port/"
      fi
      ;;
      513)
      # Rlogin
      echo "Rlogin detected. Enumerating..."
      nmap -p$port --script rlogin-brute -n "$TARGET_IP"
      
      if $ENABLE_BRUTE_FORCE; then
        echo "Brute forcing Rlogin..."
        hydra -t 4 -L /usr/share/wordlists/top100.txt -P /usr/share/wordlists/top100.txt -f -v -e nsr -s $port "$TARGET_IP" rlogin
      fi
      ;;  
    631)
      # CUPS
      echo "CUPS detected. Enumerating..."
      nmap -p$port --script cups-queue-info,cups-info -n "$TARGET_IP"
      ;;
    8080)
      # HTTP-ALT
      echo "HTTP-ALT detected. Enumerating..."
      nmap -p$port --script http-enum,http-title,http-methods,http-headers -n "$TARGET_IP"
      nikto -h "$TARGET_IP" -p $port
      dirb "http://$TARGET_IP:$port/"
      if $ENABLE_WPS; then
        wpscan --url "http://$TARGET_IP:$port/"
      fi
      ;;
    8443)
      # HTTPS-ALT
      echo "HTTPS-ALT detected. Enumerating..."
      nmap -p$port --script ssl-enum-ciphers,ssl-cert,ssl-dh-params -n "$TARGET_IP"
      nikto -h "$TARGET_IP" -p $port
      dirb "https://$TARGET_IP:$port/"
      if $ENABLE_WPS; then
        wpscan --url "https://$TARGET_IP:$port/"
      fi
      ;;
    3306)
      # MySQL
      echo "MySQL detected. Enumerating..."
      nmap -p$port --script mysql-info -n "$TARGET_IP"
      
      if $ENABLE_BRUTE_FORCE; then
        echo "Brute forcing MySQL..."
        hydra -t 4 -l root -P /usr/share/wordlists/top100.txt -f -v -e nsr -s $port "$TARGET_IP" mysql
      fi
      ;;
    3389)
      # RDP
      echo "RDP detected. Enumerating..."
      nmap -p$port --script rdp-enum-encryption,rdp-vuln-ms12-020 -n "$TARGET_IP"
      
      if $ENABLE_BRUTE_FORCE; then
        echo "Brute forcing RDP..."
        ncrack -vv --user administrator -P /usr/share/wordlists/top100.txt -p $port "$TARGET_IP"
      fi
      ;;
    5900)
      # VNC
      echo "VNC detected. Enumerating..."
      nmap -p$port --script vnc-info,vnc-title -n "$TARGET_IP"
      
      if $ENABLE_BRUTE_FORCE; then
        echo "Brute forcing VNC..."
        ncrack -vv -P /usr/share/wordlists/top100.txt -p $port "$TARGET_IP"
      fi
      ;;
    1521)
      # Oracle
      echo "Oracle detected. Enumerating..."
      nmap -p$port --script oracle-tns-version,oracle-sid-brute -n "$TARGET_IP"
      
      if $ENABLE_BRUTE_FORCE; then
        echo "Brute forcing Oracle..."
        hydra -t 4 -l sys -P /usr/share/wordlists/top100.txt -f -v -e nsr -s $port "$TARGET_IP" oracle
      fi
      ;;
    *)
      echo "Unknown service on port $port. Skipping..."
      ;;
  esac
done

for port in $ UDP_PORTS; do
  echo "Enumerating UDP port $port..."

  case $port in
    53)
      # DNS
      echo "DNS detected. Enumerating..."
      nmap -sU -p$port --script dns-nsid,dns-recursion,dns-service-discovery -n "$TARGET_IP"
      ;;
    161)
      # SNMP
      echo "SNMP detected. Enumerating..."
      nmap -sU -p$port --script snmp-brute,snmp-hh3c-logins,snmp-info,snmp-netstat,snmp-processes,snmp-sysdescr,snmp-win32-services,snmp-win32-shares -n "$TARGET_IP"
      ;;
    *)
      echo "Unknown service on UDP port $port. Skipping..."
      ;;
  esac
done

echo "Enumeration complete."
