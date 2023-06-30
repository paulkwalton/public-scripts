# Prompt the user for the target user, host, and password
$TARGET_USER = Read-Host -Prompt 'Enter the target username'
$TARGET_HOST = Read-Host -Prompt 'Enter the target host'
$TARGET_PASS = Read-Host -Prompt 'Enter the target password' -AsSecureString

# Set the local port for the SSH tunnel
$LOCAL_SOCKS_PORT="9050"

# Create the SSH tunnel using Plink
Write-Output "Creating SSH tunnel to $TARGET_USER@$TARGET_HOST on port 22..."
$secureStringPwd = ConvertFrom-SecureString -SecureString $TARGET_PASS
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($TARGET_PASS)
$PlainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
echo y | & 'C:\Program Files\PuTTY\plink.exe' -ssh -D $LOCAL_SOCKS_PORT -l $TARGET_USER -pw $PlainPassword -P 22 $TARGET_HOST
# Now Start Proxifier to route all traffic
