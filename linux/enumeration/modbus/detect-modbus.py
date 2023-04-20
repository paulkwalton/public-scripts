import os
import subprocess

def create_modbusdetect_rc(ip_address):
    content = f"""use auxiliary/scanner/scada/modbusdetect
set rhosts {ip_address}
run
"""
    with open("modbusdetect.rc", "w") as rc_file:
        rc_file.write(content)

def main():
    print("This script will enumerate if the target is using Modbus.")
    ip_address = input("Enter the target IP address: ")
    create_modbusdetect_rc(ip_address)

    print("Executing Metasploit command...")
    subprocess.run(["msfconsole", "-r", "modbusdetect.rc"])

if __name__ == "__main__":
    main()
