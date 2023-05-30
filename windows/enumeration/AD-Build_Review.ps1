cls
# Check if the ActiveDirectory module is installed
if (!(Get-Module -ListAvailable -Name ActiveDirectory)) {
    Write-Error "The ActiveDirectory module is not installed. Please install it by adding the RSAT: Active Directory Domain Services and Lightweight Directory Services Tools feature."
    exit 1
}

# Import the ActiveDirectory module
Import-Module ActiveDirectory

# Banner for Domain and Forest Functional Level
Write-Output "`n===================================="
Write-Output "Retrieving Domain and Forest Functional Level..."
Write-Output "====================================`n"

# Get Domain Functional Level
$domain = Get-ADDomain
Write-Output "Domain Functional Level is $($domain.DomainMode)"

# Get Forest Functional Level
$forest = Get-ADForest
Write-Output "Forest Functional Level is $($forest.ForestMode)"

# Banner for Domain Controller OS versions
Write-Output "`n===================================="
Write-Output "Retrieving Domain Controller OS versions..."
Write-Output "====================================`n"

# Get all Domain Controllers using Get-ADComputer cmdlet
$domainControllers = Get-ADComputer -Filter {OperatingSystem -like "*Windows Server*"} -Property OperatingSystem, OperatingSystemVersion

foreach ($dc in $domainControllers) {
    # Output the OS information for each Domain Controller
    Write-Output "Domain Controller $($dc.Name) is running $($dc.OperatingSystem) version $($dc.OperatingSystemVersion)"
}

# Banner for Computer OS versions
Write-Output "`n===================================="
Write-Output "Retrieving Computer OS versions..."
Write-Output "====================================`n"

# Define a list of obsolete operating systems
$obsoleteOperatingSystems = @("Windows Server 2003", "Windows Server 2008", "Windows Server 2008 R2", "Windows Server 2012", "Windows Server 2012 R2", "Windows 7", "Windows 8.1")

# Get all computers
$computers = Get-ADComputer -Filter * -Property OperatingSystem, OperatingSystemVersion

foreach ($computer in $computers) {
    # Check if the computer's operating system is in the list of obsolete operating systems
    if ($computer.OperatingSystem -in $obsoleteOperatingSystems) {
        Write-Output "Computer $($computer.Name) is running an obsolete OS: $($computer.OperatingSystem) version $($computer.OperatingSystemVersion)"
    } else {
        Write-Output "Computer $($computer.Name) is running $($computer.OperatingSystem) version $($computer.OperatingSystemVersion)"
    }
}

# Banner for Domain and Enterprise Administrators
Write-Output "`n===================================="
Write-Output "Retrieving Domain and Enterprise Administrators..."
Write-Output "====================================`n"

# Get Domain Administrators
$domainAdmins = Get-ADGroupMember -Identity "Domain Admins" -Recursive
Write-Output "`nDomain Administrators:"
foreach ($admin in $domainAdmins) {
    Write-Output "$($admin.samaccountname)"
}
Write-Output "`nTotal number of Domain Administrators: $($domainAdmins.Count)"

# Get Enterprise Administrators
$enterpriseAdmins = Get-ADGroupMember -Identity "Enterprise Admins" -Recursive
Write-Output "`nEnterprise Administrators:"
foreach ($admin in $enterpriseAdmins) {
    Write-Output "$($admin.samaccountname)"
}
Write-Output "`nTotal number of Enterprise Administrators: $($enterpriseAdmins.Count)"

# Banner for checking Protected Users
Write-Output "`n===================================="
Write-Output "Checking if all privileged accounts are in the 'Protected Users' group..."
Write-Output "====================================`n"

# Get Protected Users
$protectedUsers = Get-ADGroupMember -Identity "Protected Users" -Recursive

# Check Domain Administrators
Write-Output "`nChecking Domain Administrators:"
foreach ($admin in $domainAdmins) {
    if ($admin.SamAccountName -notin $protectedUsers.SamAccountName) {
        Write-Output "Domain Administrator $($admin.SamAccountName) is not in the 'Protected Users' group"
    }
}

# Check Enterprise Administrators
Write-Output "`nChecking Enterprise Administrators:"
foreach ($admin in $enterpriseAdmins) {
    if ($admin.SamAccountName -notin $protectedUsers.SamAccountName) {
        Write-Output "Enterprise Administrator $($admin.SamAccountName) is not in the 'Protected Users' group"
    }
}


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

# Banner for users with reversible password encryption
Write-Output "`n===================================="
Write-Output "Checking for users with reversible password encryption enabled..."
Write-Output "====================================`n"

# Get all users with the 'PASSWORD_REVERSIBLE' flag set
$reversiblePasswordUsers = Get-ADUser -Filter 'UserAccountControl -band 128' -Properties userAccountControl, samaccountname

# Output the users with reversible password encryption enabled
foreach ($user in $reversiblePasswordUsers) {
    Write-Output "User $($user.samaccountname) has reversible password encryption enabled"
}

# Banner for users with 'No Password Required' flag
Write-Output "`n===================================="
Write-Output "Checking for users with 'No Password Required' flag set..."
Write-Output "====================================`n"

# Get all users with the 'PASSWD_NOTREQD' flag set
$noPasswordRequiredUsers = Get-ADUser -Filter 'UserAccountControl -band 32' -Properties userAccountControl, samaccountname

# Output the users with 'No Password Required' flag set
foreach ($user in $noPasswordRequiredUsers) {
    Write-Output "User $($user.samaccountname) has 'No Password Required' flag set"
}

# Banner for checking Password Policy
Write-Output "`n===================================="
Write-Output "Checking Password Policy..."
Write-Output "====================================`n"

# Get the Default Domain Password Policy
$passwordPolicy = Get-ADDefaultDomainPasswordPolicy

# Check if the Password Policy allows passwords with less than 8 characters
if ($passwordPolicy.MinPasswordLength -lt 8) {
    Write-Output "The Password Policy allows passwords with less than 8 characters. This represents a high security risk."
} else {
    Write-Output "The Password Policy requires a minimum password length of $($passwordPolicy.MinPasswordLength) characters. This is in line with security best practices."
}

# Check if Password Complexity is enforced
if ($passwordPolicy.ComplexityEnabled) {
    Write-Output "The Password Policy enforces password complexity."
} else {
    Write-Output "The Password Policy does not enforce password complexity. Consider enabling this for stronger passwords."
}

# Check the maximum password age
if ($passwordPolicy.MaxPasswordAge -eq "-1") {
    Write-Output "The Password Policy does not specify a maximum password age."
} else {
    $maxPasswordAgeDays = $passwordPolicy.MaxPasswordAge.Days
    Write-Output "The Password Policy requires passwords to be changed every $maxPasswordAgeDays days."
}

# Banner for checking Service Accounts
Write-Output "`n===================================="
Write-Output "Checking Service Accounts..."
Write-Output "====================================`n"

# Get users with "service" or "svc" in the name and when their password was last changed
Get-ADUser -Filter {(Name -like "*service*") -or (Name -like "*svc*")} -Properties PasswordLastSet | Select-Object Name, PasswordLastSet

# Banner for checking All Accounts
Write-Output "`n===================================="
Write-Output "Checking All Accounts With Admin Bit Set..."
Write-Output "====================================`n"

# Get all accounts with admincount attribute set
Get-ADUser -Filter {AdminCount -eq 1} -Properties PasswordLastSet, AdminCount | Select-Object Name, PasswordLastSet, AdminCount

# Banner for checking Old Protocols
Write-Output "`n===================================="
Write-Output "Checking Domain Controllers support NTLMv1 and LM"
Write-Output "====================================`n"

# Get all accounts with NTLMv1 and old LM protocols enabled
Get-ADDomainController | ForEach-Object {Get-SmbServerConfiguration -CimSession $_.Name} | Select-Object PSComputerName, EnableSMB1Protocol, EnableSMB2Protocol

# Banner for checking Old Protocols
Write-Output "`n===================================="
Write-Output "Checking Domain Controllers support SMBv1"
Write-Output "====================================`n"

# Check if domain controllers support SMBv1
Get-WmiObject Win32_ServerFeature | Where-Object {$_.Name -eq "SMB1Protocol"} | Select-Object Name, DisplayName, InstalledState

# Banner for checking Administrator Accounts
Write-Output "`n===================================="
Write-Output "Checking All Administrator Accounts Which Can Be Delegated..."
Write-Output "====================================`n"

# Get the 'Administrators' group
$administratorsGroup = Get-ADGroup -Identity "Administrators"

# Get the domain of the current computer
$domain = (Get-ADDomain).DistinguishedName

# Get all members of the 'Administrators' group
$adminAccounts = Get-ADGroupMember -Identity $administratorsGroup | Where-Object { $_.objectClass -eq 'user' }

# Check each account
foreach ($account in $adminAccounts) {
    $user = Get-ADUser -Identity $account -Properties UserAccountControl

    # Check if the 'Account is sensitive and cannot be delegated' flag is not set
    $isDelegatable = -not ($user.UserAccountControl -band 0x1000000) # Bit flag for 'TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION'

    if ($isDelegatable) {
        Write-Output ("User: {0}, Can Be Delegated: {1}" -f $user.SamAccountName, $isDelegatable)
    }
}


# Banner for checking Test Accounts
Write-Output "`n===================================="
Write-Output "Checking All User Accounts for Possible Test Accounts..."
Write-Output "====================================`n"

# Specify the words to look for in account names
$words = 'test', 'dev', 'demo', 'dummy', 'sandbox', 'delete', 'trial', 'bloggs', 'doe'

# Get all user accounts
$allAccounts = Get-ADUser -Filter * -Properties SamAccountName

# Check each account
foreach ($account in $allAccounts) {
    foreach ($word in $words) {
        if ($account.SamAccountName -like "*$word*") {
            Write-Output ("Possible Test Account: {0}" -f $account.SamAccountName)
            break
        }
    }
}






