#!/bin/bash

# Exit script on error
set -e

# Ensure the script is running as root to avoid permission issues in /opt
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Navigate to /opt
cd /opt

# Clone the SharpShooter repository
echo "Cloning SharpShooter repository into /opt..."
git clone https://github.com/whale3070/SharpShooter
cd SharpShooter

# Download get-pip.py for Python 2
echo "Downloading get-pip.py for Python 2..."
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py

# Install pip for Python 2
echo "Installing pip for Python 2..."
python2 get-pip.py

# Upgrade setuptools to avoid 'egg_info' error
echo "Upgrading setuptools..."
pip2 install --upgrade setuptools

# Install the requirements from requirements.txt
echo "Installing requirements from requirements.txt..."
pip2 install -r requirements.txt

# Run SharpShooter with help flag to display usage
echo "Running SharpShooter..."
python2 SharpShooter.py -h

echo "Script completed successfully."
