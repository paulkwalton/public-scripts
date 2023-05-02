# Define the ports you want to forward
$portsToForward = @(80, 443, 4444)

# Get the WSL2 Linux host IP address
$wslIp = (wsl hostname -I).Trim()

# Get the Windows host IP address
$windowsIp = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "vEthernet (WSL)" -AddressState Preferred).IPAddress

# Configure port forwarding
ForEach ($port in $portsToForward) {
    # Remove existing port forwarding rules for the port, if any
    netsh interface portproxy reset v4tov4 listenport=$port

    # Add a new port forwarding rule
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=$windowsIp connectport=$port connectaddress=$wslIp
}

# Print the port forwarding rules
netsh interface portproxy show v4tov4

