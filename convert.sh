#!/bin/sh

if [ "$3" == "" ]; then
	sox "$1" -b 16 -r 44k "$2"
else
	sox "$1" -b 16 -r 44k "$2" fade 0:5 0 0:5
fi