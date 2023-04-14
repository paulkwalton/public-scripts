#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <target_ip>"
    exit 1
fi

TARGET_IP="$1"

# Enumerate open shares using smbclient
OPEN_SHARES=$(smbclient -N -L "$TARGET_IP" 2>/dev/null | awk '/^\s+[A-Za-z0-9]+/{print $1}' | grep -vE '^(Sharename|IPC\$)')

if [ -z "$OPEN_SHARES" ]; then
    echo "No open shares found on $TARGET_IP"
    exit 0
fi

echo "Open shares on $TARGET_IP:"
echo "=========================="
echo "$OPEN_SHARES"
echo "=========================="
echo "Listing contents of the shares:"

for SHARE in $OPEN_SHARES; do
    echo "Contents of share '$SHARE':"
    smbclient -N -c "recurse; prompt; ls" "//$TARGET_IP/$SHARE" 2>/dev/null | grep -vE '^smb\:'
    echo "=========================="
done

