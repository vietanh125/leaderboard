#!/bin/bash

# Define your SSH command
SSH_COMMAND="ssh -R leaderboard:80:localhost:7860 serveo.net"

# Function to check if SSH is running
check_ssh() {
    # Check if the SSH command is running
    if pgrep -f "$SSH_COMMAND" > /dev/null; then
        echo "SSH is running."
    else
        echo "SSH is not running. Starting SSH..."
        # Run the SSH command in the background
        $SSH_COMMAND &
        echo "SSH started."
    fi
}

# Infinite loop to continuously check SSH
while true; do
    check_ssh
    # Sleep for a desired duration before checking again (e.g., 10 seconds)
    sleep 10
done
