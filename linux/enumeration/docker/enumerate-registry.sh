#!/bin/bash

BASE_URL="http://docker-rodeo.thm:5000/v2"

# Step 1: Fetch all repositories
echo "Fetching all repositories..."
REPO_LIST=$(curl -s "${BASE_URL}/_catalog" | jq -r '.repositories[]')
echo "Repositories:"
echo "$REPO_LIST"
echo "Press enter to continue..."
read

# Loop through each repository
for REPO in $REPO_LIST; do
    echo "Fetching tags for repository: $REPO..."

    # Step 2: Fetch tags for the repository
    TAGS=$(curl -s "${BASE_URL}/${REPO}/tags/list" | jq -r '.tags[]')
    echo "Tags for $REPO:"
    echo "$TAGS"
    echo "Press enter to fetch manifests for these tags..."
    read

    # Loop through each tag
    for TAG in $TAGS; do
        echo "Fetching manifest for tag: $TAG..."

        # Step 3: Fetch manifest for the tag
        MANIFEST=$(curl -s "${BASE_URL}/${REPO}/manifests/${TAG}")
        
        # Here you can further parse the manifest as required. For simplicity, we'll just display it.
        echo "$MANIFEST"
        echo "--------------------------------------"
    done

    echo "Finished processing repository: $REPO. Press enter to continue to the next repository..."
    read
done
