import subprocess

def main():
    # Prompt user for IP address
    ip = input("Enter IP address: ")
    
    # Prompt user for username
    username = input("Enter username: ")
    
    # Prompt user for password
    password = input("Enter password: ")

    # Construct the crackmapexec command to retrieve the password policy
    # crackmapexec is a popular tool for network penetration testing
    # It supports various protocols, including SMB (Server Message Block)
    # The --pass-pol flag retrieves the password policy from the target machine
    command = f"crackmapexec smb {ip} -u {username} -p {password} --pass-pol"
    
    # Display the command being executed
    print(f"Executing command: {command}")
    
    # Execute the command using the subprocess module
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    main()
