#!/bin/bash

# Update the system
sudo yum update -y

# Install Git
sudo yum install git -y

# Install Nmap
sudo yum install nmap -y

# Install Python3 and pip if they are not installed
sudo yum install python3 python3-pip -y

# Upgrade pip to the latest version
sudo pip3 install --upgrade pip

# Install the OpenAI Python module
pip3 install openai --user

# Clone the specified GitHub repository
git clone https://github.com/paulkwalton/public-scripts.git

echo "Installation and cloning complete."
