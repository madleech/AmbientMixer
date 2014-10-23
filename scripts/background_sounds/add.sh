#!/usr/bin/env bash

. `dirname $0`/../common.sh

if [ "$1" == "" ]; then usage "$0 <filename> <sound name> - adds a new sound"; fi
if [ "$2" == "" ]; then usage "$0 <filename> <sound name> - adds a new sound"; fi

#sound['name'], sound['filename'], sound['volume']
FILENAME=`basename "$1"`
upload "$1" "sequencer" "setup_background_sounds" "" "[{\"name\":\"$2\",\"filename\":\"sounds/$FILENAME\",\"volume\":100}]"
