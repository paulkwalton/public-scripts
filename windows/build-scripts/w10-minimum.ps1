Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
# Enter Choclatry Licence Key
Start-Process notepad.exe -ArgumentList "$env:USERPROFILE\chocolatey.license.xml" -Wait
# Upgrade extension
choco upgrade chocolatey.extension
# Enable Bitlocker Disk Encryption on laptop
manage-bde -on C: -recoverypassword
mkdir c:\tools
# Install Tools Via Choc
choco install proxifier -y
choco install openoffice -y
choco install adobereader -y
choco install notepadplusplus.install -y
choco install 7zip.install -y
choco install sysinternals -y
choco install putty.install -y
choco install filezilla -y
choco install adexplorer -y
choco install nmap -y
choco install wireshark -y
choco install winscp -y
choco install -y sql-server-management-studio
choco install rsat -y
choco install python -y
choco install ida-free -y
choco install ike-scan -y
#Disable Windows Firewalls and AV
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
Add-MpPreference -ExclusionPath "C:\tools\"
#Restart the computer
Restart-Computer
