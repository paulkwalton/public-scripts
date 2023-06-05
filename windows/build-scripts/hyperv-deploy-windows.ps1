# Define Variables
$VMName = 'Windows11VM-Wintak'
$Switch = 'External Virtual Switch' 
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

# Create a new Virtual Hard Disk
New-VHD -Path $VHDPath -Dynamic -SizeBytes 256GB

# Create the Virtual Machine
New-VM -Name $VMName -MemoryStartupBytes $VMMemory -SwitchName $Switch -VHDPath $VHDPath -Generation 2 -Path "E:\Hyper-V\$VMName\" -NoVHD

# Set the VM to use Dynamic Memory
Set-VMMemory -VMName $VMName -DynamicMemoryEnabled $true

# Set the processor count for the VM
Set-VMProcessor -VMName $VMName -Count $VMProcessorCount

# Stop the VM
Stop-VM -Name $VMName -Force

# Enable nested virtualization
Set-VMProcessor -VMName $VMName -ExposeVirtualizationExtensions $true

# Mount the ISO to the VM
Add-VMDvdDrive -VMName $VMName -Path $InstallMediaPath

# Start the VM
Start-VM -Name $VMName
