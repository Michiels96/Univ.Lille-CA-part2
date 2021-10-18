#!/bin/sh
./main.py clean
./main.py dejaAmis H E
./main.py dejaAmis D E
./main.py dejaAmis E D
./main.py dejaAmis D H
./main.py dejaAmis G D
echo "scénario 1 mis en place"

# à faire:
./main.py newUser F E
#./main.py ami F G