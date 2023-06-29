# Function to check for IE proxy configuration
function Check-IEProxyConfiguration {
    $proxySettings = (Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings').ProxyEnable
    if ($proxySettings -eq 1) {
        Write-Host "Internet Explorer is configured to use a proxy."
    } else {
        Write-Host "Internet Explorer is not configured to use a proxy."
    }
}

# Function to check for internet connection by attempting to connect to a specific site
function Check-InternetConnection {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Url
    )
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        Write-Host "Successfully connected to $Url"
    } catch {
        Write-Host "Failed to connect to $Url"
    }
}

# Function to check for installed Outlook client
function Check-OutlookClient {
    $outlook = Get-WmiObject -Query "SELECT * FROM Win32_Product WHERE (Name LIKE 'Microsoft Office Outlook%')" -ErrorAction SilentlyContinue
    if ($outlook) {
        Write-Host "Outlook is installed."
    } else {
        Write-Host "Outlook is not installed."
    }
}

# Function to list download files and check the mark of the web
function Check-DownloadFilesAndMotW {
    # Get the path to all user profile directories
    $UserProfileDirs = Get-ChildItem 'C:\Users' | Where-Object { $_.PSIsContainer }

    # Loop through each user profile directory
    foreach ($UserProfileDir in $UserProfileDirs) {
        $DownloadsDir = Join-Path -Path $UserProfileDir.FullName -ChildPath 'Downloads'

        # Check if the Downloads directory exists
        if (Test-Path -Path $DownloadsDir) {
            # Get the files in the Downloads directory
            $Files = Get-ChildItem -Path $DownloadsDir -File

            # Loop through each file and print its details
            foreach ($File in $Files) {
                # Check for the 'Mark of the Web'
                $zoneIdentifierPath = $File.FullName + ':Zone.Identifier'
                if (Test-Path -Path $zoneIdentifierPath) {
                    $MotW = Get-Content -Path $zoneIdentifierPath
                    Write-Host ("User: " + $UserProfileDir.Name + ", File: " + $File.Name + ", Mark of the Web: " + $MotW)
                } else {
                    Write-Host ("User: " + $UserProfileDir.Name + ", File: " + $File.Name + ", Mark of the Web: Not present")
                }
            }
        }
    }
}

# Check for IE proxy configuration
Check-IEProxyConfiguration

# Check for internet connection
Check-InternetConnection -Url 'http://www.google.com'

# Check for installed Outlook client
Check-OutlookClient

# Check download files and Mark of the Web
Check-DownloadFilesAndMotW
