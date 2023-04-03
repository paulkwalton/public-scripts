clear
Write-Host @"
 _   _ _____ _____ _   _ ________   __
| \ | |_   _|_   _| \ | |__  / _ \ / /_
|  \| | | |   | | |  \| | / / | | | '_ \
| |\  | | |   | | | |\  |/ /| |_| | (_) |
|_| \_| |_|   |_| |_| \_/____\___/ \___/
                                        
Pentest Cleanup Tool

Press any key to continue...
"@ -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

clear

# Define the list of standard files and folders
$standardItems = @(
    'Documents and Settings',
    'Program Files',
    'Program Files (x86)',
    'ProgramData',
    'Users',
    'Windows',
    'PerfLogs',
    'Recovery',
    'System Volume Information',
    'hiberfil.sys',
    'pagefile.sys',
    'swapfile.sys'
)

Write-Host "Checking for non-standard files and folders in the root of C:..." -ForegroundColor Cyan

# Get the items in the root of C:
$rootItems = Get-ChildItem -Path "C:\" -Force

# Iterate through the items and check if they are in the standard list
foreach ($item in $rootItems) {
    if ($standardItems -notcontains $item.Name) {
        Write-Host " - Found non-standard item:" $item.FullName -ForegroundColor Red
    }
}


# Get startup items from the common startup folder
Write-Host "Check startup items from the common startup folder:" -ForegroundColor Cyan
$commonStartupFolderPath = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
$commonStartupItems = Get-ChildItem $commonStartupFolderPath

foreach ($item in $commonStartupItems) {
    Write-Host " -" $item.Name -ForegroundColor Red
}

# Get startup items from the Run registry keys for all users
Write-Host "`nCheck startup items from the Run registry keys for all users:" -ForegroundColor Cyan
$runRegistryPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
$runRegistryItems = Get-ItemProperty $runRegistryPath

foreach ($item in $runRegistryItems.PSObject.Properties) {
    Write-Host " -" $item.Name -ForegroundColor Red
}

# Get startup items from the Run registry keys for the current user
Write-Host "`nCheck startup items from the Run registry keys for the current user:" -ForegroundColor Cyan
$runRegistryPathCU = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
$runRegistryItemsCU = Get-ItemProperty $runRegistryPathCU

foreach ($item in $runRegistryItemsCU.PSObject.Properties) {
    Write-Host " -" $item.Name -ForegroundColor Red
}

# Get all user profile paths
$userProfilePaths = Get-ChildItem 'C:\Users' -Directory

# Initialize an empty array to store startup items from user profiles
$userProfileStartupItems = @()

# Loop through each user profile and get startup items
foreach ($userProfile in $userProfilePaths) {
    Write-Host "`nStartup items from user profile:" $userProfile.Name -ForegroundColor Cyan
    $startupFolderPath = Join-Path $userProfile.FullName "AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
    
    if (Test-Path $startupFolderPath) {
        $startupItems = Get-ChildItem $startupFolderPath

        foreach ($item in $startupItems) {
            Write-Host " -" $item.Name -ForegroundColor Red
        }
    } else {
        Write-Host "No startup items found for this user." -ForegroundColor Green
    }
}


# Check if the PsExec service is running
Write-Host "Checking if PsExec service is running..." -ForegroundColor Cyan
$psexecService = Get-Service -Name "PSEXESVC" -ErrorAction SilentlyContinue

if ($psexecService -and $psexecService.Status -eq "Running") {
    Write-Hosst "PsExec service is running. Please investigate:" -ForegroundColor Red
    $psexecService | Format-Table Name, DisplayName, Status
} else {
    Write-Host "PsExec service is not running." -ForegroundColor Green
}


Write-Host "Checking if Recycle Bin is empty..." -ForegroundColor Cyan
$shell = New-Object -ComObject Shell.Application
$recycleBin = $shell.Namespace(0xA)
$recycleBinItems = $recycleBin.Items()

if ($recycleBinItems.Count -gt 0) {
    Write-Host "Recycle Bin is not empty. Please empty the Recycle Bin." -ForegroundColor Red
}

Write-Host "Get the local Administrators group members..." -ForegroundColor Cyan
$administrators = Get-LocalGroupMember -Name "Administrators"

foreach ($administrator in $administrators) {
    Write-Host " -" $administrator -ForegroundColor Red
}

Write-Host "Get the local Users..." -ForegroundColor Cyan
$localUsers = Get-LocalUser

foreach ($localUser in $localUsers) {
    Write-Host " -" $localUser.Name -ForegroundColor Red
}



Write-Host "Check if Windows Defender service is running..." -ForegroundColor Cyan
# Check if Windows Defender service is running
$windowsDefenderService = Get-Service -Name "WinDefend" -ErrorAction SilentlyContinue

if (!$windowsDefenderService -or $windowsDefenderService.Status -ne "Running") {
    Write-Host "Windows Defender service is not running. This must be restarted" -ForegroundColor Red
} else {
    Write-Host "Windows Defender service is running."
}


Write-Host "Check if FireEye and Tanium agents are running..." -ForegroundColor Cyan
# Check if FireEye and Tanium agents are running
$fireEyeService = Get-Service -Name "FireEyeAgent" -ErrorAction SilentlyContinue
$taniumService = Get-Service -Name "TaniumClient" -ErrorAction SilentlyContinue

if (!$fireEyeService -or $fireEyeService.Status -ne "Running") {
    Write-Host "FireEye agent is not running. This must be restarted" -ForegroundColor Red
} else {
    Write-Host "FireEye agent is running."
}

if (!$taniumService -or $taniumService.Status -ne "Running") {
    Write-Host "Tanium agent is not running. This must be restarted" -ForegroundColor Red
} else {
    Write-Host "Tanium agent is running."
}

# Set the path to the root directory you want to search
Write-Host "Checking for LSASS dump files. This will take some time!" -ForegroundColor Cyan
$rootPath = "C:\"

# Get all user profile paths
$userProfilePaths = Get-ChildItem 'C:\Users' -Directory

# Initialize an empty array to store LSASS dump files
$lsassDumpFiles = @()

# Loop through each user profile and search for LSASS dump files
foreach ($userProfile in $userProfilePaths) {
    $tempPath = Join-Path $userProfile.FullName 'AppData\Local\Temp\*.dmp'
    $foundFiles = Get-ChildItem $tempPath -Include "*.dmp" -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*lsass*" }
    if ($foundFiles) {
        $lsassDumpFiles += $foundFiles
    }
}

if ($lsassDumpFiles) {
    Write-Host "LSASS dump files found. Please delete them immediately:" -ForegroundColor Red
    $lsassDumpFiles | Format-Table FullName
} else {
    Write-Host "No LSASS dump files found." -ForegroundColor Green
}

Write-Host "Searching for left over pentest artifacts..." -ForegroundColor Cyan

$fileExtensions = "*.ps1","*.py", "*.exe","*.bat", "*.txt", "*.psm", "*.msi"

$searchKeywords = "pentest", "powerup", "psexec", "pingcastle", "putty", "chisel","exploit", "payload", "backdoor", "mimikatz", "hashcat", "burp", "nessus","empire", "msfvenom", "shellter", "beacon", "sliver"

$searchKeywords = $searchKeywords | Select-Object -Unique

$userProfilePaths = Get-ChildItem 'C:\Users' -Directory

$foundItems = @()

foreach ($userProfile in $userProfilePaths) {
    $profilePath = $userProfile.FullName
    $items = Get-ChildItem $profilePath -Recurse -Include $fileExtensions -ErrorAction SilentlyContinue

    $filteredItems = $items | Where-Object {
        $nameMatches = $searchKeywords | Where-Object {
            $_.Name -match $searchKeyword
        }
        $contentMatches = $false
        if ($_.Attributes -ne "Directory") {
            try {
                $contentMatches = $_ | Select-String -Pattern $searchKeywords -SimpleMatch -Quiet
            } catch {
                Write-Warning "Could not read the content of file $($_.FullName)"
            }
        }
        return $nameMatches -or $contentMatches
    }

    if ($filteredItems) {
        $foundItems += $filteredItems
    }
}

if ($foundItems) {
    Write-Host "Found potential pentest artifacts:"
    $foundItems | Format-Table FullName
} else {
    Write-Host "No pentest artifacts found." -ForegroundColor Green
}






Read-Host -Prompt "Press Enter to exit"

