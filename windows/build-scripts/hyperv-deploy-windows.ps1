# Define Variables
$VMName = 'Windows11VM'
$Switch = 'default Switch' 
$InstallMediaPath = 'E:\ISO\windows11.iso'
$VHDPath = "E:\Hyper-V\$VMName\Virtual Hard Disks\$VMName.vhdx"
$VMMemory = 8GB
$VMProcessorCount = 12

# Check if the VM already exists
if (Get-VM -Name $VMName -ErrorAction SilentlyContinue) {
    # Stop the VM
    Stop-VM -Name $VMName -Force -TurnOff
    # Remove the VM
    Remove-VM -Name $VMName -Force
}

# Create a new folder for the VM
New-Item -Path "E:\Hyper-V\$VMName\Virtual Hard Disks\" -ItemType Directory -Force

# Check if the VHD file already exists
if (Test-Path $VHDPath) {
    # Delete the VHD file
    Remove-Item -Path $VHDPath -Force
}

# Create a new Virtual Hard Disk
New-VHD -Path $VHDPath -Dynamic -SizeBytes 256GB

# Create the Virtual Machine
New-VM -Name $VMName -MemoryStartupBytes $VMMemory -SwitchName $Switch -VHDPath $VHDPath -Generation 2 -Path "E:\Hyper-V\$VMName\"

# Set the VM to use Dynamic Memory
Set-VMMemory -VMName $VMName -DynamicMemoryEnabled $true

# Set the processor count for the VM
Set-VMProcessor -VMName $VMName -Count $VMProcessorCount

# Stop the VM
Stop-VM -Name $VMName -Force

# Enable nested virtualization
Set-VMProcessor -VMName $VMName -ExposeVirtualizationExtensions $true

# Create a key protector for the VM
$owner = Get-HgsGuardian -Name "UntrustedGuardian"
$kp = New-HgsKeyProtector -Owner $owner -AllowUntrustedRoot

# Apply the key protector to the VM
Set-VMKeyProtector -VMName $VMName -KeyProtector $kp.RawData

# Enable TPM for the VM
Enable-VMTPM -VMName $VMName

# Enable Guest Services
Enable-VMIntegrationService -VMName $VMName -Name 'Guest Service Interface'

# Enable TPM
Enable-VMTPM -VMName $VMName

# Mount the ISO to the VM
Add-VMDvdDrive -VMName $VMName -Path $InstallMediaPath

# Set CD as highest boot order
$DVDDrive = Get-VMDvdDrive -VMName $VMName
Set-VMFirmware -VMName $VMName -FirstBootDevice $DVDDrive

# Start the VM
Start-VM -Name $VMName

