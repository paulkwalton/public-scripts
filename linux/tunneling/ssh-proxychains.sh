#!/bin/bash

# Prompt the user for the target user, host, and password
read -p "Enter the target username: " TARGET_USER
read -p "Enter the target host: " TARGET_HOST
read -s -p "Enter the target password: " TARGET_PASS
echo

# Set the local port for the SSH tunnel
LOCAL_SOCKS_PORT="9050"

# Check for any existing SSH tunnels on port 8080 and terminate them
EXISTING_TUNNEL_PIDS=$(lsof -ti :$LOCAL_SOCKS_PORT)
if [ ! -z "$EXISTING_TUNNEL_PIDS" ]; then
  echo "Terminating existing SSH tunnel(s) on port $LOCAL_SOCKS_PORT..."
  kill $EXISTING_TUNNEL_PIDS
fi

# Create the SSH tunnel
echo "Creating SSH tunnel to $TARGET_USER@$TARGET_HOST on port 22..."
sshpass -p "$TARGET_PASS" ssh -f -N -D $LOCAL_SOCKS_PORT -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $TARGET_USER@$TARGET_HOST -p 22

if [ $? -eq 0 ]; then
  echo "SSH tunnel created successfully. You can now use proxychains manually."
else
  echo "Failed to create SSH tunnel."
  exit 1
fi

