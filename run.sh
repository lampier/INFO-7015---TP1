#!/bin/sh

if [ $# < 1 ]
then
	echo "Wrong number of arguments. To see the help page pass in 'h' as the first argument"
	exit
fi

echo "Running this script will delete all the text files and png files in this directory and create new ones. Do you want to proceed? [y/n]"

read answer 

if [ "$answer" = "y" ]
then

	python main.py -t 10 -i 5 -n 320 -s 16 -r 2
		

fi


