#!/bin/bash

# This script runs play.py with varying 'gain' values from 0.1 to 2.5 with a step of 0.1

# Starting value
start=0.1
# Ending value
end=2.5
# Step
step=0.1

# Use a while loop to increment the 'gain' value
current=$start
while (( $(echo "$current <= $end" | bc -l) )); do
    echo "Running with gain=$current"
    python3 play.py --gain=$current --operator=pid
    # Increment current gain
    current=$(echo "$current + $step" | bc)
done
