#!/bin/sh

. `dirname $0`/../common.sh

if [ "$1" == "" ]; then usage "$0 <sound> <volume 0-100> - adjusts volume of the specified sound"; fi

send "sound" "vol" "$1" $2
