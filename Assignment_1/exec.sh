#!/bin/bash

# Timeout value in seconds
timeout_val=60

# Memory limit in KB (adjust as needed)
memory_limit=1  # 10MB

# Function to check memory usage
check_memory_usage() {
    # Get memory usage of the process
    mem_usage=$(ps -p $pid -o rss=)
    if [[ $mem_usage -gt $memory_limit ]]; then
        echo "Memory usage exceeded $((memory_limit)) KB. Terminating..."
        kill -9 $pid
        exit 1
    fi
}

# Loop through instance files i01 to i10
for ((i=1; i<=10; i++))
do
    instance="Instances/i$(printf "%02d" $i)"  # Format instance number with leading zero if necessary

    # Execute command for current instance with timeout and memory usage check
    output=$(timeout $timeout_val bash -c '
        python pacman.py "$1" &
        pid=$!
        while [ "$(ps -p $pid -o pid=)" ]; do
            check_memory_usage
        done
    ' bash "$instance" 2>&1)

    # Check if the command timed out
    if [[ $? -eq 124 ]]; then
        echo "Instance $instance timed out after $timeout_val seconds"
        continue
    fi

    # Check if the command was terminated due to memory usage
    if [[ $? -eq 1 ]]; then
        continue
    fi

    # Extract information from output
    ixx="i$(printf "%02d" $i)"
    execution_time=$(echo "$output" | grep "Execution time" | cut -f2)
    nodes_explored=$(echo "$output" | grep "#Nodes explored" | cut -f2)
    queue_size=$(echo "$output" | grep "Queue size at goal" | cut -f2)

    # Display information
    echo "Instance: $ixx"
    echo "Execution time: $execution_time"
    echo "#Nodes explored: $nodes_explored"
    echo "Queue size at goal: $queue_size"
    echo ""
done
