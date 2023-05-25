Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
# Remove all the Windows Bloatware
mkdir c:\tools
# Install Tools Via Choc
choco install bginfo -y
choco install adobereader -y
choco install googlechrome -y
choco install firefox -y
choco install notepadplusplus.install -y
choco install 7zip.install -y
choco install sysinternals -y
choco install putty.install -y
choco install filezilla -y
choco install adexplorer -y
choco install nmap -y
choco install wireshark -y
choco install winscp -y
choco install vnc-viewer -y
choco install -y keepass.install
choco install -y postman
choco install -y sql-server-management-studio
choco install -y tor-browser
choco install rsat -y
choco install python -y
choco install golang -y
choco install keepassx -y
choco install angryip -y
choco install vlc -y
choco install teamviewer -y
#Clone Tools From Github
Write-Output "Download & Install Spiderfoot"
git clone https://github.com/smicallef/spiderfoot.git c:\tools\spiderfoot
cd c:\tools\spiderfoot
pip install -r requirements.txt
Write-Output "Download Github Tooling"
git clone https://github.com/PowerShellMafia/PowerSploit.git c:\tools\powersploit
git clone https://github.com/carlospolop/PEASS-ng.git c:\tools\linux\peass-ng
git clone https://github.com/rebootuser/LinEnum.git c:\tools\linux\linenum
git clone https://github.com/dafthack/MailSniper.git c:\tools\mailsniper
git clone https://github.com/dafthack/DomainPasswordSpray.git c:\tools\domainpasswordspray
git clone https://github.com/Kevin-Robertson/Inveigh.git c:\tools\inveigh
git clone https://github.com/adrecon/ADRecon.git c:\tools\adrecon
git clone https://github.com/GhostPack/Rubeus.git c:\tools\rubeus
git clone https://github.com/GhostPack/Seatbelt.git c:\tools\seatbelt
git clone https://github.com/GhostPack/SharpUp.git c:\tools\sharpup
git clone https://github.com/GhostPack/Certify.git c:\tools\certify
git clone https://github.com/cube0x0/SharpMapExec.git c:\tools\sharpmapexec
git clone https://github.com/Flangvik/NetLoader.git c:\tools\netloader
git clone https://github.com/BloodHoundAD/AzureHound c:\tools\azurehound
git clone https://github.com/nyxgeek/o365recon.git c:\tools\office365recon
# To Execute WinPWN Import-Module .\WinPwn.ps1 Or iex(new-object net.webclient).downloadstring('https://raw.githubusercontent.com/S3cur3Th1sSh1t/WinPwn/master/WinPwn.ps1')
git clone https://github.com/S3cur3Th1sSh1t/WinPwn.git c:\tools\winpwn
git clone https://github.com/dafthack/MSOLSpray.git c:\tools\msolspray
git clone https://github.com/offensive-security/exploitdb.git c:\tools\exploitdb-source
git clone https://github.com/offensive-security/exploitdb-bin-sploits.git c:\tools\exploitdb-bin
git clone https://github.com/danielbohannon/Invoke-Obfuscation.git c:\tools\invoke-obfuscation
git clone https://github.com/gentilkiwi/mimikatz.git c:\tools\mimikatz
git clone https://github.com/CCob/SweetPotato.git c:\tools\sweetpotato
git clone https://github.com/XenocodeRCE/neo-ConfuserEx.git c:\tools\neoconfuserex
git clone https://github.com/yck1509/ConfuserEx.git c:\tools\confuserex
git clone https://github.com/danielmiessler/SecLists.git c:\tools\seclists
git clone https://github.com/rasta-mouse/ThreatCheck.git c:\tools\threatcheck
git clone https://github.com/JohnWoodman/remoteInjector.git c:\tools\remoteinjector
git clone https://github.com/mandiant/SharPersist.git c:\tools\sharppersist
git clone https://github.com/BloodHoundAD/BloodHound.git c:\tools\bloodhound
git clone https://github.com/BloodHoundAD/SharpHound.git c:\tools\sharphound
git clone https://github.com/CCob/SweetPotato.git c:\tools\sweetpotato
git clone https://github.com/Dec0ne/KrbRelayUp.git c:\tools\krbrelayup
git clone https://github.com/WazeHell/vulnerable-AD.git c:\tools\vulnerable-AD
git clone https://github.com/haseebT/mRemoteNG-Decrypt.git c:\tools\mRemoteNG-Decrypt
git clone https://github.com/mgeeky/PackMyPayload.git c:\tools\packmypayload
git clone https://github.com/skahwah/SQLRecon.git c:\tools\sqlrecon
git clone https://github.com/GhostPack/SafetyKatz.git c:\tools\safetykatz
# Disable Windows Firewalls
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
# Restart Windows & rename Windows
Write-Output "Rename & Reboot Windows"
Rename-Computer -NewName "WinTak"
Restart-Computer

