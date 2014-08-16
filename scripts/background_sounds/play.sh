#!/bin/sh

. `dirname $0`/../common.sh

if [ "$1" == "" ]; then usage "$0 <sound> - plays the specified background sound"; fi

args=("$@")
send "background_sound" "play" "$1"
