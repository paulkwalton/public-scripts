Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
# Enter Choclatry Licence Key
Start-Process notepad.exe -ArgumentList "$env:USERPROFILE\chocolatey.license.xml" -Wait
# Upgrade extension
choco upgrade chocolatey.extension
# Disable RDP
Set-ItemProperty -Path ‘HKLM:\System\CurrentControlSet\Control\Terminal Server’-name “fDenyTSConnections” -Value 1
# Enable Bitlocker Disk Encryption on laptop
manage-bde -on C: -recoverypassword
mkdir c:\tools
# Install Tools Via Choc
choco install proxifier -y
choco install openoffice -y
choco install burp-suite-pro-edition -y
choco install zap -y
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
choco install solarwinds-tftp-server -y

# Disable Windows Firewalls and AV
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
Add-MpPreference -ExclusionPath "C:\tools\"
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
git clone https://github.com/paulkwalton/public-scripts.git c:\tools\public-scripts
git clone https://github.com/antonioCoco/RogueWinRM.git c:\tools\roguewinrm
git clone https://github.com/itm4n/PrivescCheck.git c:\tools\PrivescCheck
git clone https://github.com/wavestone-cdt/powerpxe.git c:\tools\powerpxe
git clone https://github.com/vdohney/keepass-password-dumper.git c:\tools\keepass-password-dumper
Invoke-WebRequest -Uri "https://download.sysinternals.com/files/AccessChk.zip" -OutFile "C:\tools\AccessChk.zip"
Invoke-WebRequest -Uri "https://github.com/vletoux/pingcastle/releases/download/3.1.0.1/PingCastle_3.1.0.1.zip" -OutFile "C:\tools\PingCastle_3.1.0.1.zip"
Invoke-WebRequest -Uri "https://download.sysinternals.com/files/ProcessMonitor.zip" -OutFile "C:\tools\ProcessMonitor.zip"


This command will download the `ProcessMonitor.zip` file and save it to the `C:\tools\` directory. Ensure the directory exists before executing the command.
# Restart Windows & rename Windows
Write-Output "Rename & Reboot Windows"
Rename-Computer -NewName "WinTak"

# Create the directory if it does not exist
if (!(Test-Path -Path "C:\temp\")) {
    New-Item -ItemType Directory -Force -Path "C:\temp\"
}

# Enable Windows Subsystem for Linux (WSL)
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart


# Self-deleting
$MyPath = $MyInvocation.MyCommand.Path
$DeleteScriptBlock = { param($path) Start-Sleep -Seconds 2; Remove-Item -Path $path }
Start-Job -ScriptBlock $DeleteScriptBlock -ArgumentList $MyPath

# Define the PostRestartScript content
$PostRestartScriptContent = @"
# Set WSL 2 as your default version
wsl --set-default-version 2
# Download and install the Linux kernel update package
`$kernelUpdateUrl = "https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi"
`$kernelUpdateFile = "C:\temp\wsl_update_x64.msi"
Invoke-WebRequest -Uri `$kernelUpdateUrl -OutFile `$kernelUpdateFile
Start-Process -FilePath `$kernelUpdateFile -Wait
Restart-Computer
"@

# Create PostRestartScript.ps1
$PostRestartScriptContent | Out-File -FilePath 'C:\temp\PostRestartScript.ps1'

# Copy the PostRestartScript.ps1 to the Desktop
Copy-Item -Path 'C:\temp\PostRestartScript.ps1' -Destination "$([Environment]::GetFolderPath('Desktop'))\RunMeAfterReboot.ps1"

# Restart the computer
choco install docker-desktop -y
Restart-Computer
