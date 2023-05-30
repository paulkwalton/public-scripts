cls

# Check if the ActiveDirectory module is installed
if (!(Get-Module -ListAvailable -Name ActiveDirectory)) {
    Write-Error "The ActiveDirectory module is not installed. Please install it by adding the RSAT: Active Directory Domain Services and Lightweight Directory Services Tools feature."
    exit 1
}

# Import the ActiveDirectory module
Import-Module ActiveDirectory

# Banner for Domain and Forest Functional Level
Write-Host "======================================" -ForegroundColor Green
Write-Host "  Retrieving Domain and Forest Functional Level...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green

# Get Domain Functional Level
$domain = Get-ADDomain
Write-Host "Domain Functional Level is $($domain.DomainMode)" -ForegroundColor Yellow

# Get Forest Functional Level
$forest = Get-ADForest
Write-Host "Forest Functional Level is $($forest.ForestMode)" -ForegroundColor Yellow


Write-Host "`n======================================" -ForegroundColor Green
Write-Host "  Checking Active Directory Trusts...  " -ForegroundColor White
Write-Host "======================================`n" -ForegroundColor Green

# Get all trusts
$trusts = Get-ADTrust -Filter *

# Check if trusts exist
if($trusts) {
    # Output the trusts
    foreach ($trust in $trusts) {
        Write-Host ("Trust Name: {0}, Trust Direction: {1}, Trust Type: {2}" -f $trust.Name, $trust.TrustDirection, $trust.TrustType) -ForegroundColor Yellow
    }
} else {
    Write-Host "No Active Directory trusts found." -ForegroundColor Yellow
}


Write-Host "======================================" -ForegroundColor Green
Write-Host "  Retrieving Domain Controller OS versions...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get all Domain Controllers using Get-ADComputer cmdlet
$domainControllers = Get-ADComputer -Filter {OperatingSystem -like "*Windows Server*"} -Property OperatingSystem, OperatingSystemVersion

foreach ($dc in $domainControllers) {
    # Output the OS information for each Domain Controller
    Write-Host "Domain Controller $($dc.Name) is running $($dc.OperatingSystem) version $($dc.OperatingSystemVersion)" -ForegroundColor Yellow
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Retrieving Computer OS versions...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Define a list of obsolete operating systems
$obsoleteOperatingSystems = @("Windows Server 2003", "Windows Server 2008", "Windows Server 2008 R2", "Windows Server 2012", "Windows Server 2012 R2", "Windows 7", "Windows 8.1")

# Get all computers
$computers = Get-ADComputer -Filter * -Property OperatingSystem, OperatingSystemVersion

foreach ($computer in $computers) {
    # Check if the computer's operating system is in the list of obsolete operating systems
    if ($computer.OperatingSystem -in $obsoleteOperatingSystems) {
        Write-Host "Computer $($computer.Name) is running an obsolete OS: $($computer.OperatingSystem) version $($computer.OperatingSystemVersion)" -ForegroundColor Red
    } else {
        Write-Host "Computer $($computer.Name) is running $($computer.OperatingSystem) version $($computer.OperatingSystemVersion)" -ForegroundColor Yellow
    }
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Retrieving Domain and Enterprise Administrators...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get Domain Administrators
$domainAdmins = Get-ADGroupMember -Identity "Domain Admins" -Recursive
Write-Host "Domain Administrators:" -ForegroundColor Yellow
foreach ($admin in $domainAdmins) {
    Write-Output "$($admin.samaccountname)"
}
Write-Host "Total number of Domain Administrators: $($domainAdmins.Count)" -ForegroundColor Yellow

# Get Enterprise Administrators
$enterpriseAdmins = Get-ADGroupMember -Identity "Enterprise Admins" -Recursive
Write-Output "Enterprise Administrators:"
foreach ($admin in $enterpriseAdmins) {
    Write-Output "$($admin.samaccountname)"
}
Write-Host "Total number of Enterprise Administrators: $($enterpriseAdmins.Count)" -ForegroundColor Yellow

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking Schema Admins Group...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get the 'Schema Admins' group
$schemaAdminsGroup = Get-ADGroup -Identity "Schema Admins"

# Get the members of the 'Schema Admins' group
$schemaAdmins = Get-ADGroupMember -Identity $schemaAdminsGroup

if ($schemaAdmins) {
    Write-Host "WARNING: 'Schema Admins' group is not empty. Current members:" -ForegroundColor Red
    foreach ($admin in $schemaAdmins) {
        Write-Host ("Name: {0}, SID: {1}" -f $admin.Name, $admin.SID) -ForegroundColor Yellow
    }
} else {
    Write-Output "'Schema Admins' group is empty."
}


Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking All Users and Groups with admin' in Name...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get all user accounts with 'admin' in the name
$adminUsers = Get-ADUser -Filter { Name -like '*admin*' } | Select-Object Name, SamAccountName

# Get all groups with 'admin' in the name
$adminGroups = Get-ADGroup -Filter { Name -like '*admin*' } | Select-Object Name

# Print the results
Write-Host "`nUsers with 'admin' in name:" -ForegroundColor Yellow
$adminUsers | ForEach-Object { Write-Host $_.Name }

Write-Host "`nGroups with 'admin' in name:" -ForegroundColor Yellow
$adminGroups | ForEach-Object { Write-Host $_.Name }


Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking if all privileged accounts are in the 'Protected Users' group...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get Protected Users
$protectedUsers = Get-ADGroupMember -Identity "Protected Users" -Recursive
Write-Host "`nProtected Users:" -ForegroundColor Yellow
$protectedUsers | ForEach-Object { Write-Host $_.Name }

# Check Domain Administrators
Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking if Domain Admin accounts are in the 'Protected Users' group...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green
foreach ($admin in $domainAdmins) {
    if ($admin.SamAccountName -notin $protectedUsers.SamAccountName) {
        Write-Output "Domain Administrator $($admin.SamAccountName) is not in the 'Protected Users' group"
    }
}

# Check Enterprise Administrators
Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking if Enterprise Admin accounts are in the 'Protected Users' group...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green
foreach ($admin in $enterpriseAdmins) {
    if ($admin.SamAccountName -notin $protectedUsers.SamAccountName) {
        Write-Output "Enterprise Administrator $($admin.SamAccountName) is not in the 'Protected Users' group"
    }
}

# Banner for AS-REP Roasting
Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking for users vulnerable to AS-REP Roasting...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get all users with the 'DONT_REQUIRE_PREAUTH' flag set
$asrepUsers = Get-ADUser -Filter 'UserAccountControl -band 4194304' -Properties userAccountControl, samaccountname

# Output the users vulnerable to AS-REP Roasting
foreach ($user in $asrepUsers) {
    Write-Host "User $($user.samaccountname) is vulnerable to AS-REP Roasting" -ForegroundColor Red
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking for potential Kerberoastable users...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get all users with a set Service Principal Name
$kerberoastUsers = Get-ADUser -Filter {ServicePrincipalName -like "*"} -Properties ServicePrincipalName, samaccountname

# Output the Kerberoastable users
foreach ($user in $kerberoastUsers) {
    Write-Host "User $($user.samaccountname) may be Kerberoastable" -ForegroundColor Red
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking for users with 'Password Never Expires' set...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get all users with 'Password Never Expires' flag set
$passwordNeverExpiresUsers = Get-ADUser -Filter {PasswordNeverExpires -eq $true} -Properties PasswordNeverExpires, samaccountname

# Output the users with 'Password Never Expires' set
foreach ($user in $passwordNeverExpiresUsers) {
    Write-Host "User $($user.samaccountname) has 'Password Never Expires' set" -ForegroundColor Red
}



Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking for inactive users (90 days without login)...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get date for 90 days ago
$dateCutoff = (Get-Date).AddDays(-90)

# Get all users that have not logged in for 90 days
$inactiveUsers = Get-ADUser -Filter {LastLogonDate -lt $dateCutoff} -Properties LastLogonDate, samaccountname

# Output the inactive users
foreach ($user in $inactiveUsers) {
    Write-Output "User $($user.samaccountname) has been inactive since $($user.LastLogonDate)"
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking for disabled users...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get all disabled users
$disabledUsers = Get-ADUser -Filter {Enabled -eq $false} -Properties Enabled, samaccountname

# Output the disabled users
foreach ($user in $disabledUsers) {
    Write-Output "User $($user.samaccountname) is disabled"
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking for locked out users...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green

# Get Locked Out Users
$lockedOutUsers = Search-ADAccount -LockedOut
Write-Output "Locked Out Users:"
foreach ($user in $lockedOutUsers) {
    Write-Output "$($user.samaccountname)"
}
Write-Output "Total number of Locked Out Users: $($lockedOutUsers.Count)"

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Users created in the last 7 days  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green

Get-ADUser -Filter {whenCreated -ge ((Get-Date).AddDays(-7)).Date}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking for users with reversible password encryption enabled...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get all users with the 'PASSWORD_REVERSIBLE' flag set
$reversiblePasswordUsers = Get-ADUser -Filter 'UserAccountControl -band 128' -Properties userAccountControl, samaccountname

# Output the users with reversible password encryption enabled
foreach ($user in $reversiblePasswordUsers) {
    Write-Host "User $($user.samaccountname) has reversible password encryption enabled" -ForegroundColor Red
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking for users with 'No Password Required' flag set...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get all users with the 'PASSWD_NOTREQD' flag set
$noPasswordRequiredUsers = Get-ADUser -Filter 'UserAccountControl -band 32' -Properties userAccountControl, samaccountname

# Output the users with 'No Password Required' flag set
foreach ($user in $noPasswordRequiredUsers) {
    Write-Host "User $($user.samaccountname) has 'No Password Required' flag set" -ForegroundColor Red
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking Password Policy...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


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

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking Service Accounts Operating As User Accounts...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get users with "service" or "svc" in the name and when their password was last changed
Get-ADUser -Filter {(Name -like "*service*") -or (Name -like "*svc*")} -Properties PasswordLastSet | Select-Object Name, PasswordLastSet

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking Backup Accounts...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get users with "backup" or "bkp" in the name and when their password was last changed
Get-ADUser -Filter {(Name -like "*backup*") -or (Name -like "*bkp*")} -Properties PasswordLastSet | Select-Object Name, PasswordLastSet

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking All Accounts With Admin Bit Set...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get all accounts with admincount attribute set
Get-ADUser -Filter {AdminCount -eq 1} -Properties PasswordLastSet, AdminCount | Select-Object Name, PasswordLastSet, AdminCount

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking Domain Controllers support NTLMv1 and LM  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get all accounts with NTLMv1 and old LM protocols enabled
Get-ADDomainController | ForEach-Object {Get-SmbServerConfiguration -CimSession $_.Name} | Select-Object PSComputerName, EnableSMB1Protocol, EnableSMB2Protocol

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking Domain Controllers support SMBv1  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green

# Check if domain controllers support SMBv1
Get-WmiObject Win32_ServerFeature | Where-Object {$_.Name -eq "SMB1Protocol"} | Select-Object Name, DisplayName, InstalledState

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking All Administrator Accounts Which Can Be Delegated...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


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


Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking All User Accounts for Possible Test Accounts...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Specify the words to look for in account names
$words = 'test', 'dev', 'demo', 'dummy', 'sandbox', 'delete', 'trial', 'bloggs', 'doe', 'old', 'remove', 'pentest', '1234'

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

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking All OUs for Delegations to 'Everyone' or 'Authenticated Users'...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get all OUs
$OUs = Get-ADOrganizationalUnit -Filter * -Properties nTSecurityDescriptor

foreach ($OU in $OUs) {
    # Get the ACL for the OU
    $acl = Get-Acl -Path ("AD:\" + $OU.DistinguishedName)

    # Check if there is any Access Rule for 'Everyone' or 'Authenticated Users'
    foreach ($accessRule in $acl.Access) {
        if ($accessRule.IdentityReference.Value -eq "Everyone" -or $accessRule.IdentityReference.Value -eq "NT AUTHORITY\Authenticated Users") {
            Write-Output ("WARNING: OU '{0}' has delegation for '{1}'" -f $OU.Name, $accessRule.IdentityReference.Value)
        }
    }
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking krbtgt Password Last Set...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get the krbtgt account
$krbtgt = Get-ADUser -Identity "krbtgt" -Properties PasswordLastSet

# Get the current date
$now = Get-Date

# Calculate the time since the password was last set
$monthsSinceLastSet = (($now - $krbtgt.PasswordLastSet).Days) / 30

# Check if the password was last set more than 6 months ago
if ($monthsSinceLastSet -gt 6) {
    Write-Output ("WARNING: krbtgt password was last set on {0}, which is more than 6 months ago." -f $krbtgt.PasswordLastSet)
} else {
    Write-Output ("krbtgt password was last set on {0}." -f $krbtgt.PasswordLastSet)
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking Anonymous LDAP...  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get the RootDSE information for the current domain
$rootDSE = Get-ADRootDSE

# Get the domain policy object
$domainPolicy = Get-ADObject -Identity ($rootDSE.defaultNamingContext) -Properties dSHeuristics

# Check the dSHeuristics attribute
if ($domainPolicy.dSHeuristics -eq $null) {
    Write-Output "Anonymous LDAP is DISABLED."
} elseif ($domainPolicy.dSHeuristics.Substring(0,1) -eq "2") {
    Write-Output "Anonymous LDAP is DISABLED."
} else {
    Write-Output "WARNING: Anonymous LDAP is ENABLED."
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Checking Windows 2000 Preauth Accounts (everyone or anonymous is bad)  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


Get-ADGroupMember -Identity "CN=Pre-Windows 2000 Compatible Access,CN=Builtin,$((Get-ADDomain).DistinguishedName)" | Get-ADUser -Server $((Get-ADDomain).DnsRoot) | Select-Object Name,SamAccountName | Sort-Object Name

Write-Host "======================================" -ForegroundColor Green
Write-Host "  DNSAdmins Abuse.  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


Get-ADGroupMember -Identity DNSAdmins | Select-Object Name,SamAccountName | Sort-Object Name

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Backup Operator Abuse.  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


Get-ADGroupMember -Identity "Backup Operators" | Select-Object Name,SamAccountName | Sort-Object Name

Get-ADObject -filter { (UserAccountControl -BAND 0x0080000) -OR (UserAccountControl -BAND 0x1000000) -OR (msDS-AllowedToDelegateTo -like '*') } -prop Name,ObjectClass,PrimaryGroupID,UserAccountControl,ServicePrincipalName,msDS-AllowedToDelegateTo

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Has AD Administrator Account Been Renamed  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


$Domain = Get-ADDomain

# Get the SID for the domain's Administrator account
$AdminSID = $Domain.DomainSID.Value + "-500"

# Get the Administrator account
$AdminAccount = Get-ADUser -Filter { SID -eq $AdminSID }

# Check if the Administrator account has been renamed
if ($AdminAccount.SamAccountName -eq "Administrator") {
    Write-Output "The AD administrator account has not been renamed."
} else {
    Write-Output "The AD administrator account has been renamed to $($AdminAccount.SamAccountName)."
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Has LAPS been enforced  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green

# Get all computer objects
$Computers = Get-ADComputer -Filter * -Properties ms-Mcs-AdmPwdExpirationTime

# Check if LAPS is enforced for each computer
foreach ($Computer in $Computers) {
    if ($null -ne $Computer.'ms-Mcs-AdmPwdExpirationTime') {
        Write-Output "LAPS is enforced for $($Computer.Name)."
    } else {
        Write-Output "LAPS is not enforced for $($Computer.Name)."
    }
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Has Recycle Bin Been Enabled  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green


# Get the current forest
$forest = Get-ADForest

# Get the Recycle Bin optional feature
$recycleBin = Get-ADOptionalFeature 'Recycle Bin Feature' -Server $forest.SchemaMaster

# Check if the Recycle Bin is enabled
if ($recycleBin.EnabledScopes -contains $forest.ForestMode) {
    Write-Output "The AD Recycle Bin is enabled."
} else {
    Write-Output "The AD Recycle Bin is not enabled."

$scriptTitle = "SQL Server Enumeration via Active Directory PowerShell"
Write-Host "======================================" -ForegroundColor Green
Write-Host "  $scriptTitle  " -ForegroundColor White
Write-Host "======================================" -ForegroundColor Green

# Find all SQL Servers registered in AD
$sqlServers = Get-ADObject -Filter 'objectClass -eq "serviceConnectionPoint"' -Property keywords |
    Where-Object { $_.keywords -like "*MSSQL*" } |
    ForEach-Object { $_.DistinguishedName }

# Check if any SQL servers were found
if ($sqlServers) {
    Write-Host "SQL Servers found:" -ForegroundColor Yellow
    Write-Host ($sqlServers -join "")
} else {
    Write-Host "No SQL Servers found." -ForegroundColor Red
}





}

