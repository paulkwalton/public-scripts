# Define the ports you want to forward
$portsToForward = @(80, 443, 4444, 8080, 8888)

# Get the WSL2 Linux host IP address
$wslIp = (wsl hostname -I).Trim()

# Reset all existing port forwarding rules
Write-Host "Resetting all existing rules..."
netsh interface portproxy reset

# Get all Windows IPv4 addresses
$windowsIPs = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.*" -and $_.IPAddress -notlike "127.*"}

ForEach ($windowsIP in $windowsIPs) {

    $currentWindowsIp = $windowsIP.IPAddress

    # Configure port forwarding
    ForEach ($port in $portsToForward) {
        Write-Host "Configuring port forwarding for port: $port"

        # Add a new port forwarding rule
        Write-Host "Adding new rule for $currentWindowsIp..."
        $addResult = netsh interface portproxy add v4tov4 listenport=$port listenaddress=$currentWindowsIp connectport=$port connectaddress=$wslIp
        Write-Host $addResult
    }
}

# Print the port forwarding rules
Write-Host "Current port forwarding rules:"
netsh interface portproxy show v4tov4



