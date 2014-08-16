#!/bin/sh

. `dirname $0`/../common.sh

if [ "$1" == "" ]; then usage "$0 <sound> <frequency> - determines how often the sound will play"; fi

send "sound" "freq" $1 $2
