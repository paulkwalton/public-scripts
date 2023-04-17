import subprocess

# Get user input
domain = input("Enter domain: ")
username = input("Enter username: ")
password = input("Enter password: ")
dc = input("Enter domain controller: ")

# Run GetADUsers.py command
cmd = f"GetADUsers.py -all {domain}/{username}:{password} -dc-ip {dc}"
result = subprocess.check_output(cmd, shell=True).decode("utf-8")

# Output only usernames
for line in result.splitlines():
    if line.strip() and not line.startswith("  "):
        print(line.split()[0])
