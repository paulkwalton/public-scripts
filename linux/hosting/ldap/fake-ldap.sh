sudo apt-get update && sudo apt-get -y install slapd ldap-utils && sudo systemctl enable slapd
sudo dpkg-reconfigure -p low slapd
echo -e "dn: cn=config\nreplace: olcSaslSecProps\nolcSaslSecProps: noanonymous,minssf=0,passcred" > /opt/olcSaslSecProps.ldif
sudo ldapmodify -Y EXTERNAL -H ldapi:// -f /opt/olcSaslSecProps.ldif && sudo service slapd restart

