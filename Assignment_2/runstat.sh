#! /bin/bash

PYTHON_WIN="python"
PYTHON_UNIX="python3"

# Check if the OS is Windows, else UNIX
if [ "$OS" = "Windows_NT" ]; then
    PYHON_TO_USE=$PYTHON_WIN
else
    PYHON_TO_USE=$PYTHON_UNIX
fi
# Set opponents
OPPONENT_WHITE="alphabeta" # random | alphabeta | mcts | agent | human
OPPONENT_BLACK="mcts"

# Initialize CSV file with header
echo "Winner,Moves,Time" > alphabeta_vs_random.csv

# Run 10 games with white as alphabeta and black as random
for i in {1..10}; do
    echo "Running game $i with white as $OPPONENT_WHITE and black as $OPPONENT_BLACK"
    START=$(date +%s.%N)
    OUTPUT=$(python3 LINFO1361-Shobu/main.py -l log.txt -w $OPPONENT_WHITE -b $OPPONENT_BLACK)
    if [ $? -ne 0 ]; then
        echo "Error executing the Python script."
        exit 1
    fi
    END=$(date +%s.%N)
    WINNER=$(echo "$OUTPUT" | grep "Winner" | cut -d ":" -f 2 | tr -d ' ' | cut -d "," -f 1)
    MOVES=$(echo "$OUTPUT" | grep "n_moves" | cut -d "," -f 2 | tr -d ' ' | cut -d ":" -f 2)
    TIME=$(echo "$END - $START" | bc)
    echo "$WINNER,$MOVES,$TIME" >> alphabeta_vs_mcts.csv
done

# Swap opponents
OPPONENT_WHITE="mcts"
OPPONENT_BLACK="alphabeta"

# Initialize CSV file with header
echo "Winner,Moves,Time" > random_vs_alphabeta.csv

# Run 10 games with white as random and black as alphabeta
for i in {1..10}; do
    echo "Running game $i with white as $OPPONENT_WHITE and black as $OPPONENT_BLACK"
    START=$(date +%s.%N)
    OUTPUT=$(python3 LINFO1361-Shobu/main.py -l log.txt -w $OPPONENT_WHITE -b $OPPONENT_BLACK)
    if [ $? -ne 0 ]; then
        echo "Error executing the Python script."
        exit 1
    fi
    END=$(date +%s.%N)
    WINNER=$(echo "$OUTPUT" | grep "Winner" | cut -d ":" -f 2 | tr -d ' ' | cut -d "," -f 1)
    MOVES=$(echo "$OUTPUT" | grep "n_moves" | cut -d "," -f 2 | tr -d ' ' | cut -d ":" -f 2)
    TIME=$(echo "$END - $START" | bc)
    echo "$WINNER,$MOVES,$TIME" >> mcts_vs_alphabeta.csv
done


# End of file