#!/bin/sh

. `dirname $0`/../common.sh

if [ "$1" == "" ]; then usage "$0 <sound> <0/1> - enable/disable looping of a sound"; fi

send "sound" "loop" $1 $2
