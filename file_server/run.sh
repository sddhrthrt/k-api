#!/bin/bash

DATAPATH='https://gist.githubusercontent.com/deliahu/65894dd2a65e74aec8e09f78f03fee8f/raw/3100f18b4c968d04a256205ac5149e135ce84513/README.md'
if [ $# -gt 0 ]
then
	DATAPATH=$1
fi

APIPATH='/test'
if [ $# -gt 1 ]
then
	APIPATH=$2
fi

curl -Ss $DATAPATH > file.txt

python file_server.py $APIPATH
