#!/bin/bash
# If using a shell executed via a remote ssg login, this will keep the shell alive and stop any timeouts.

# Define the SSH config file path
SSH_CONFIG="$HOME/.ssh/config"

# Check if .ssh directory exists, if not create it
if [ ! -d "$HOME/.ssh" ]; then
    mkdir "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"
fi

# Check if config file exists, if not create it
if [ ! -f "$SSH_CONFIG" ]; then
    touch "$SSH_CONFIG"
    chmod 600 "$SSH_CONFIG"
fi

# Check if config already has ServerAliveInterval and ServerAliveCountMax
if ! grep -q "ServerAliveInterval" "$SSH_CONFIG" && ! grep -q "ServerAliveCountMax" "$SSH_CONFIG"; then
    echo "Host *" >> "$SSH_CONFIG"
    echo "    ServerAliveInterval 60" >> "$SSH_CONFIG"
    echo "    ServerAliveCountMax 120" >> "$SSH_CONFIG"
else
    echo "Config already has ServerAliveInterval and/or ServerAliveCountMax"
fi

# Restart SSH service
# This will differ based on the system. 
# Debian-based systems (including Ubuntu) usually use 'service', Fedora/RHEL-based systems use 'systemctl'.
# Use which command is appropriate for your system.

# For Debian/Ubuntu systems:
sudo service ssh restart

# For Fedora/RHEL systems:
# sudo systemctl restart sshd
