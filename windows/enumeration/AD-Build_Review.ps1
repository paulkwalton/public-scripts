# Check if the ActiveDirectory module is installed
if (!(Get-Module -ListAvailable -Name ActiveDirectory)) {
    Write-Error "The ActiveDirectory module is not installed. Please install it by adding the RSAT: Active Directory Domain Services and Lightweight Directory Services Tools feature."
    exit 1
}

# Import the ActiveDirectory module
Import-Module ActiveDirectory

# Banner for AS-REP Roasting
Write-Output "`n===================================="
Write-Output "Checking for users vulnerable to AS-REP Roasting..."
Write-Output "====================================`n"

# Get all users with the 'DONT_REQUIRE_PREAUTH' flag set
$asrepUsers = Get-ADUser -Filter 'UserAccountControl -band 4194304' -Properties userAccountControl, samaccountname

# Output the users vulnerable to AS-REP Roasting
foreach ($user in $asrepUsers) {
    Write-Output "User $($user.samaccountname) is vulnerable to AS-REP Roasting"
}

# Banner for Kerberoastable users
Write-Output "`n===================================="
Write-Output "Checking for potential Kerberoastable users..."
Write-Output "====================================`n"

# Get all users with a set Service Principal Name
$kerberoastUsers = Get-ADUser -Filter {ServicePrincipalName -like "*"} -Properties ServicePrincipalName, samaccountname

# Output the Kerberoastable users
foreach ($user in $kerberoastUsers) {
    Write-Output "User $($user.samaccountname) may be Kerberoastable"
}

# Banner for 'Password Never Expires' users
Write-Output "`n===================================="
Write-Output "Checking for users with 'Password Never Expires' set..."
Write-Output "====================================`n"

# Get all users with 'Password Never Expires' flag set
$passwordNeverExpiresUsers = Get-ADUser -Filter {PasswordNeverExpires -eq $true} -Properties PasswordNeverExpires, samaccountname

# Output the users with 'Password Never Expires' set
foreach ($user in $passwordNeverExpiresUsers) {
    Write-Output "User $($user.samaccountname) has 'Password Never Expires' set"
}

# Banner for inactive users
Write-Output "`n===================================="
Write-Output "Checking for inactive users (90 days without login)..."
Write-Output "====================================`n"

# Get date for 90 days ago
$dateCutoff = (Get-Date).AddDays(-90)

# Get all users that have not logged in for 90 days
$inactiveUsers = Get-ADUser -Filter {LastLogonDate -lt $dateCutoff} -Properties LastLogonDate, samaccountname

# Output the inactive users
foreach ($user in $inactiveUsers) {
    Write-Output "User $($user.samaccountname) has been inactive since $($user.LastLogonDate)"
}

# Banner for disabled users
Write-Output "`n===================================="
Write-Output "Checking for disabled users..."
Write-Output "====================================`n"

# Get all disabled users
$disabledUsers = Get-ADUser -Filter {Enabled -eq $false} -Properties Enabled, samaccountname

# Output the disabled users
foreach ($user in $disabledUsers) {
    Write-Output "User $($user.samaccountname) is disabled"
}

# Banner for users with reversible password
