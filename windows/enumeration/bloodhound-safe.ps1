Write-Output @"
============================================================
Welcome to the BloodHound File Execution and Archiving Script!

This PowerShell script does the following:

1. Prompts you for the location of the BloodHound executable (.exe) file.
2. Checks if the file exists.
3. Asks for your desired output directory.
4. Checks if the output directory exists.
5. Generates a timestamp, which is used to name the output zip file.
6. Creates a 10-character alphanumeric password randomly.
7. Runs the BloodHound exe file with specific parameters including the generated zip file name and password.
8. Outputs the randomly generated password for your zip file.

Key Features:
- BloodHound is run in Stealth mode. This is designed to minimize the amount of noise generated in logs, making it less likely to trigger alerts.
- BloodHound is also run in DC Only mode. This means that it will only collect information about Domain Controllers, reducing the amount of data collected and processed.

These features make the tool more efficient and stealthy, enabling it to operate without attracting unnecessary attention.

Please follow the prompts and provide accurate information when requested.
Let's get started!
============================================================
"@
# Add assembly for creating Windows Forms
Add-Type -AssemblyName System.Windows.Forms

# Create OpenFileDialog for exe file selection
$openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
$openFileDialog.Filter = "Exe Files (*.exe)|*.exe"
$openFileDialog.Title = "Please select your executable file"
$openFileDialog.ShowDialog() | Out-Null
$exeLocation = $openFileDialog.FileName

# Check if the exe file exists
if (-not (Test-Path $exeLocation -PathType Leaf)) {
    Write-Output "The specified exe file does not exist. Please provide a valid file path."
    return
}

# Set the output directory to the user's Documents folder
$outputDirectory = [Environment]::GetFolderPath("MyDocuments")

# Generate a timestamp for the output folder name
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$outputSubDirectory = Join-Path -Path $outputDirectory -ChildPath $timestamp

# Create a new subdirectory with the timestamp
New-Item -ItemType Directory -Force -Path $outputSubDirectory

# Run the exe with the specified parameters
& "$exeLocation" --CollectionMethods DCOnly --Stealth --OutputDirectory "$outputSubDirectory" --RandomFilenames
