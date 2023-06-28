import os
import subprocess

def create_modbus_findunitid_rc(ip_address):
    content = f"""use auxiliary/scanner/scada/modbus_findunitid
set rhosts {ip_address}
run
"""
    with open("modbus_findunitid.rc", "w") as rc_file:
        rc_file.write(content)

def main():
    print("This script will find the Unit ID for a Modbus target.")
    ip_address = input("Enter the target IP address: ")
    create_modbus_findunitid_rc(ip_address)

    print("Executing Metasploit command...")
    subprocess.run(["msfconsole", "-r", "modbus_findunitid.rc"])

if __name__ == "__main__":
    main()
