# Define the ports you want to forward
$portsToForward = @(80, 443, 4444, 8080)

# Get the WSL2 Linux host IP address
$wslIp = (wsl hostname -I).Trim()

# Get the Windows host IP address
$windowsIp = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "vEthernet (WSL)" -AddressState Preferred).IPAddress

# Reset all existing port forwarding rules
Write-Host "Resetting all existing rules..."
netsh interface portproxy reset

# Configure port forwarding
ForEach ($port in $portsToForward) {
    Write-Host "Configuring port forwarding for port: $port"

    # Add a new port forwarding rule
    Write-Host "Adding new rule..."
    $addResult = netsh interface portproxy add v4tov4 listenport=$port listenaddress=$windowsIp connectport=$port connectaddress=$wslIp
    Write-Host $addResult
}

# Print the port forwarding rules
Write-Host "Current port forwarding rules:"
netsh interface portproxy show v4tov4


