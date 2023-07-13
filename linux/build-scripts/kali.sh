echo "Updating Kali Linux..."
sudo apt update -y
sudo apt full-upgrade -y
# Kali Hardening Section <Starts>
echo "Installing security updates..."
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
echo "Removing unnecessary services..."
sudo systemctl disable --now bluetooth.service
sudo systemctl disable --now avahi-daemon.service
sudo systemctl disable --now cups.service
sudo systemctl disable --now isc-dhcp-server.service
sudo systemctl disable --now isc-dhcp-server6.service
sudo systemctl disable --now slapd.service
sudo systemctl disable --now nfs-server.service
sudo systemctl disable --now bind9.service
sudo systemctl disable --now vsftpd.service
sudo systemctl disable --now dovecot.service
sudo systemctl disable --now smbd.service
sudo systemctl disable --now squid.service
sudo systemctl disable --now snmpd.service
# Install and configure Fail2Ban
echo "Installing and configuring Fail2Ban..."
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
# Create a basic Fail2Ban configuration for SSH
echo "Creating a basic Fail2Ban configuration for SSH..."
echo "
[sshd]
enabled  = true
port     = ssh
filter   = sshd
logpath  = /var/log/auth.log
maxretry = 3
bantime  = 86400
" | sudo tee /etc/fail2ban/jail.d/ssh.local
sudo systemctl restart fail2ban
echo "Installing and running RKHunter to check for rootkits..."
sudo apt install rkhunter -y
echo Check For Rootkits Using RKHunter
sudo rkhunter -c -sk
echo "Kali Linux hardening completed."
# Kali Hardening Section <End>
echo "Installing various packages..."
sudo apt install -y kali-linux-default
sudo apt install leafpad -y
sudo apt install default-jdk -y
sudo apt install build-essential -y
sudo apt install windows-binaries -y 
curl https://i.jpillora.com/chisel! | bash
echo "Setting up and starting SSH server..."
sudo apt install openssh-server -y
sudo systemctl enable ssh.service
sudo systemctl start ssh.service
echo "Installing various packages..."
sudo mkdir -p /opt/sysinternals/
sudo wget -O /opt/sysinternals/sysinternals.zip https://download.sysinternals.com/files/SysinternalsSuite.zip 
sudo mkdir -p /opt/privesc/linux
sudo wget -O /opt/privesc/linux/linpeas.sh https://github.com/carlospolop/PEASS-ng/releases/download/20220814/linpeas.sh
sudo mkdir -p /opt/privesc/windows
sudo wget -O /opt/privesc/windows/linpeas.bat https://github.com/carlospolop/PEASS-ng/releases/download/20220814/winPEAS.bat
sudo mkdir -p /opt/buildreview
sudo mkdir -p /opt/password
sudo mkdir -p /opt/network
sudo mkdir -p /opt/persistence/
echo "Cloning repositories into /opt directory..."
sudo git clone https://github.com/paulkwalton/public-scripts.git /opt/scripts/
sudo git clone https://github.com/edernucci/identity-to-hashcat.git /opt/identity-to-hashcat
sudo git clone https://github.com/Ridter/cve-2020-0688.git /opt/exploits/cve-2020-0688
sudo git clone https://github.com/rebootuser/LinEnum.git /opt/privesc/linux/linenum
sudo git clone https://github.com/bitsadmin/wesng.git /opt/privesc/windows/exploit-suggester
sudo git clone https://github.com/nccgroup/ScoutSuite.git /opt/auditing/cloud/scoutsuite
sudo git clone https://github.com/Mebus/cupp.git /opt/password/cupp
sudo git clone https://github.com/r3motecontrol/Ghostpack-CompiledBinaries.git /opt/privesc/windows/ghostpack
sudo git clone https://gchq.github.io/CyberChef/ /opt/gchq-cyberchef
sudo git clone https://github.com/ropnop/kerbrute /opt/adtools/kerbrute
sudo git clone https://github.com/sc0tfree/updog.git /opt/filehosting
sudo git clone https://github.com/Flangvik/SharpCollection.git /opt/sharpcollection
sudo git clone https://github.com/phra/PEzor.git /opt/PEzor
sudo git clone https://github.com/fortra/nanodump.git /opt/bof/nanodump
sudo git clone https://github.com/FortyNorthSecurity/RandomScripts.git /opt/shellcode-formatter
sudo git clone https://github.com/hashcat/kwprocessor.git /opt/kwprocessor
sudo git clone https://github.com/dirkjanm/PrivExchange.git /opt/PrivExchange
sudo git clone https://github.com/mdsecactivebreach/Chameleon.git /opt/chameleon
sudo git clone https://github.com/Arvanaghi/SessionGopher.git /opt/privesc/windows/sessiongopher
sudo git clone https://github.com/411Hall/JAWS.git /opt/privesc/windows/jaws
sudo git clone https://github.com/rasta-mouse/Sherlock.git /opt/privesc/windows/sherlock
sudo git clone https://github.com/AlessandroZ/BeRoot.git /opt/privesc/windows/beroot
sudo git clone https://github.com/antonioCoco/RemotePotato0.git /opt/privesc/windows/remotepotato
sudo git clone https://github.com/OneLogicalMyth/BuildReview-Windows.git /opt/buildreview/buildreview-windows
sudo git clone https://github.com/OneLogicalMyth/PAudit.git /opt/buildreview/paudit
sudo git clone https://github.com/gentilkiwi/mimikatz.git /opt/password/mimikatz
sudo git clone https://github.com/GhostPack/KeeThief.git /opt/password/keethief
sudo git clone https://github.com/gentilkiwi/kekeo.git /opt/password/kekeo
sudo git clone https://github.com/leoloobeek/LAPSToolkit.git /opt/password/lapstoolkit
sudo git clone https://github.com/fox-it/BloodHound.py.git /opt/adtools/BloodHoundPY
sudo git clone https://github.com/kmahyyg/mremoteng-decrypt.git /opt/remoteng-decrypt
sudo wget -O /opt/network/putty.exe https://the.earth.li/~sgtatham/putty/latest/w64/putty.exe
sudo wget -O /opt/network/winscp.exe https://winscp.net/download/files/2023010513098bec75153682d04acc7dafc6c99d5ae2/WinSCP-5.21.6-Portable.zip
sudo wget -O /opt/icspasswords/scada.csv https://github.com/ITI/ICS-Security-Tools/blob/f829a32f98fadfa5206d3a41fc3612dd4741c8b3/configurations/passwords/scadapass.csv
sudo wget -O /opt/network/kerbrute-linux-64 https://github.com/ropnop/kerbrute/releases/download/v1.0.3/kerbrute_linux_amd64
sudo wget -O /opt/network/proxifierpe.zip https://www.proxifier.com/download/ProxifierPE.zip
sudo wget -O /opt/network/proxifier.zip https://www.proxifier.com/download/ProxifierSetup.exe
sudo git clone https://github.com/p0dalirius/Coercer.git /opt/network/coercer
sudo git clone https://github.com/Sw4mpf0x/PowerLurk.git /opt/persistence/windows/powerlurk
sudo git clone https://github.com/3ndG4me/spraygen.git /opt/passwordspry-creator
sudo git clone https://github.com/ITI/ICS-Security-Tools.git /opt/ics/resources
sudo git clone https://github.com/lgandx/PCredz.git /opt/packetcapture/pcredz
git clone --recursive https://github.com/BC-SECURITY/Empire.git -y
echo "Installing KWprocessor and generating keyboard walk passwords..."
cd /opt/kwprocessor/
sudo make
./kwp -z basechars/full.base keymaps/en-us.keymap routes/2-to-16-max-3-direction-changes.route > /opt/keyboard-walk-passwords.txt
sudo mkdir -p opt/adtools/sharphound
sudo wget -O /opt/adtools/sharphound/sharphound.ps1 https://github.com/BloodHoundAD/BloodHound/raw/master/Collectors/SharpHound.ps1
sudo wget -O /opt/adtools/sharphound.exe https://github.com/BloodHoundAD/BloodHound/raw/master/Collectors/SharpHound.exe
sudo wget -O /opt/adtools/pingcastle https://github.com/vletoux/pingcastle/releases/download/3.0.0.0/PingCastle_3.0.0.0.zip
sudo wget -O /opt/adtools/windapsearch https://github.com/ropnop/go-windapsearch/releases/download/v0.3.0/windapsearch-linux-amd64
sudo wget -O /opt/expressvpn https://www.expressvpn.works/clients/linux/expressvpn_3.30.0.2-1_amd64.deb
sudo wget -O /opt/chisel https://github.com/jpillora/chisel/releases/download/v1.7.7/chisel_1.7.7_linux_amd64.gz
sudo wget -O /opt/ruler-linux64 https://github.com/sensepost/ruler/releases/download/2.4.1/ruler-linux64
sudo mkdir -p /opt/gophish/
sudo wget -O /opt/gophish/gophish-v0.12.1-linux-64bit.zip https://github.com/gophish/gophish/releases/download/v0.12.1/gophish-v0.12.1-linux-64bit.zip
sudo git clone https://github.com/attackdebris/kerberos_enum_userlists.git /opt/wordlists/kerberos_enum_userlists
sudo apt-get install wget gpg -y
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
rm -f packages.microsoft.gpg
echo "Installing various tools using apt-get..."
sudo apt install apt-transport-https -y
sudo apt update -y
sudo apt install code -y
sudo apt install wpscan -y
sudo wpscan --update 
sudo apt install macchanger -y
sudo apt install python3-impacket -y
sudo apt install git -y
sudo apt install netcat-traditional -y
sudo apt install powershell  -y
sudo apt install shellter -y
sudo apt install netcat -y
sudo apt install tilix -y
sudo apt install sqlmap -y
sudo apt install gobuster -y
sudo apt install iputils-ping -y
sudo apt install dirbuster -y
sudo apt install dirb -y
sudo apt install nano -y
sudo apt install nikto -y
sudo apt install sublist3r -y
sudo apt install zeek -y
sudo apt install net-tools -y
sudo apt install exploitdb -y
sudo apt install novnc -y
sudo apt install tcpdump -y
sudo apt install msfpc -y
sudo apt install smbclient -y
sudo apt install lldpd -y
sudo service lldpd start
sudo apt install enum4linux -y
sudo apt install default-mysql-client -y
sudo gem install highline -y
sudo apt install snapd -y
sudo apt install prips -y
sudo apt install dirsearch -y
sudo apt install pip -y
sudo apt install rdesktop -y
sudo apt install seclists -y
sudo apt install dnsrecon -y
sudo apt install jython -y
sudo apt install sqlitebrowser -y
sudo apt install hashid -y
sudo apt install spray -y
sudo apt install bloodhound -y
sudo apt install responder -y
sudo apt install yersinia -y
sudo apt install spiderfoot -y
sudo apt install amass-common -y
sudo apt install psql -y
sudo apt install neo4j -y
sudo apt install gobuster -y
sudo apt install auditd audispd-plugins -y
sudo apt install -y kali-win-kex
sudo pip install mitm6
sudo pip install pyftpdlib
apt install golang-go -y
go mod vendor
sudo apt install libpcap-dev -y
pip3 install Cython
pip3 install python-libpcap
#Request Section for new apps
sudo dpkg -i mysql-apt-config_0.5.3-1_all.deb
sudo apt update -y
sudo apt install mysql-workbench-community -y
sudo apt install sshpass -y
sudo git clone https://github.com/CISOfy/lynis.git /opt/lynis
sudo apt install eyewitness -y
sudo apt install hping3 -y
sudo git clone https://github.com/secdev/scapy.git /opt/scapy 
sudo apt install wafw00f -y
sudo git clone https://github.com/sc0tfree/updog.git /opt/updog
dpkg --add-architecture i386 && apt-get update -y && apt-get install wine32:i386 -y
sudo gem install evil-winrm
sudo apt update -y
sudo apt autoremove -y
sudo updatedb
sudo service postgresql start
echo "Changing default SSH keys..."
sudo mkdir /etc/ssh/old_keys
sudo mv /etc/ssh/ssh_host_* /etc/ssh/old_keys
sudo dpkg-reconfigure openssh-server
sudo macchanger -A eth0
echo "Installing xfce4 & xrdp and configuring xrdp to listen to port 3390..."
apt-get install -y kali-desktop-xfce xorg xrdp
echo "[i] Configuring xrdp to listen to port 3390 (but not starting the service)"
sed -i 's/port=3389/port=3390/g' /etc/xrdp/xrdp.ini
sudo systemctl enable xrdp --now
# Write a file which confirms the build script has reached the end, and not fell over.
touch /opt/script-completed-pls-del-me.txt
echo "Enabling Apache2 modules..."
sudo a2enmod rewrite
sudo a2enmod proxy 
sudo a2enmod proxy_http 
sudo a2enmod proxy_balancer 
sudo a2enmod lbmethod_byrequests
echo "Installing Sliver C2 framework..."
sudo curl https://sliver.sh/install|sudo bash
echo "Manually installing VMware tools to allow VMware folder redirection..."
kali-tweaks
# Restart Kali, and good to go.
kex --win -s
