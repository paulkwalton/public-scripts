 # Download 7-Zip installer
$7zipUrl = "https://www.7-zip.org/a/7z2301-x64.exe"
$7zipFile = "c:\tools\7zInstaller.exe"
Invoke-WebRequest -Uri $7zipUrl -OutFile $7zipFile

# Install 7-Zip and wait for the installer to complete
Start-Process $7zipFile -Wait

# Download Notepad++ installer
$notepadUrl = "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.5.8/npp.8.5.8.Installer.x64.exe"
$notepadFile = "c:\tools\NotepadPlusPlusInstaller.exe"
Invoke-WebRequest -Uri $notepadUrl -OutFile $notepadFile

# Install Notepad++ and wait for the installer to complete
Start-Process $notepadFile -Wait

# Download Sysinternals Suite
$sysinternalsUrl = "https://download.sysinternals.com/files/SysinternalsSuite.zip"
$sysinternalsFile = "c:\tools\SysinternalsSuite.zip"
Invoke-WebRequest -Uri $sysinternalsUrl -OutFile $sysinternalsFile

# Extract Sysinternals Suite
$destinationPath = "C:\tools\"  # Replace with the path where you want to extract the files
Expand-Archive -Path $sysinternalsFile -DestinationPath $destinationPath -Force

# Download PuTTY installer
$puttyUrl = "https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.79-installer.msi"
$puttyFile = "c:\tools\PuttyInstaller.msi"
Invoke-WebRequest -Uri $puttyUrl -OutFile $puttyFile

# Install PuTTY and wait for the installer to complete
Start-Process $puttyFile -Wait

# Download Nmap installer
$nmapUrl = "https://nmap.org/dist/nmap-7.94-setup.exe"
$nmapFile = "C:\tools\NmapInstaller.exe"
Invoke-WebRequest -Uri $nmapUrl -OutFile $nmapFile

# Install Nmap and wait for the installer to complete
Start-Process $nmapFile -Wait

# Download WinSCP installer
$winscpUrl = "https://winscp.net/download/WinSCP-6.1.2-Setup.exe"
$winscpFile = "C:\tools\WinSCPInstaller.exe"
Invoke-WebRequest -Uri $winscpUrl -OutFile $winscpFile

# Install WinSCP and wait for the installer to complete
Start-Process $winscpFile -Wait

# Download SSMS installer
$ssmsUrl = "https://aka.ms/ssmsfullsetup"
$ssmsFile = "C:\tools\SSMSInstaller.exe"
Invoke-WebRequest -Uri $ssmsUrl -OutFile $ssmsFile

# Install SSMS and wait for the installer to complete
Start-Process $ssmsFile -Wait

# Download Visual Studio Code installer
$vsCodeUrl = "https://code.visualstudio.com/sha/download?build=stable&os=win32-user"
$vsCodeFile = "C:\tools\VSCodeInstaller.exe"
Invoke-WebRequest -Uri $vsCodeUrl -OutFile $vsCodeFile

# Install Visual Studio Code and wait for the installer to complete
Start-Process $vsCodeFile -Wait

# Download Git for Windows installer
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe"
$gitFile = "C:\tools\GitInstaller.exe"
Invoke-WebRequest -Uri $gitUrl -OutFile $gitFile

# Install Git for Windows and wait for the installer to complete
Start-Process $gitFile -Wait

git clone https://github.com/Azure/azure-storage-azcopy.git c:\tools\

# Cyberduck
$cyberduckUrl = "https://update.cyberduck.io/windows/Cyberduck-Installer-8.7.0.40629.exe"
$cyberduckFile = "C:\tools\CyberduckInstaller.exe"
Invoke-WebRequest -Uri $cyberduckUrl -OutFile $cyberduckFile
Start-Process $cyberduckFile -Wait

# Fiddler
$fiddlerUrl = "https://www.telerik.com/download/fiddler/fiddler-everywhere-windows"
$fiddlerFile = "C:\tools\FiddlerInstaller.exe"
Invoke-WebRequest -Uri $fiddlerUrl -OutFile $fiddlerFile
Start-Process $fiddlerFile -Wait

# HeidiSQL
$heidiSqlUrl = "https://www.heidisql.com/installers/HeidiSQL_12.5.0.6677_Setup.exe"
$heidiSqlFile = "C:\tools\HeidiSQLInstaller.exe"
Invoke-WebRequest -Uri $heidiSqlUrl -OutFile $heidiSqlFile
Start-Process $heidiSqlFile -Wait

# HXD
$hadUrl = "https://mh-nexus.de/downloads/HxDSetup.zip"
$hadFile = "C:\tools\HADInstaller.exe"
Invoke-WebRequest -Uri $hadUrl -OutFile $hadFile
Start-Process $hadFile -Wait

# Kubernetes CLI
$kubernetesCliUrl = "https://dl.k8s.io/release/v1.28.3/bin/windows/amd64/kubectl.exe"
$kubernetesCliFile = "C:\tools\Kubectl.exe"
Invoke-WebRequest -Uri $kubernetesCliUrl -OutFile $kubernetesCliFile











 
