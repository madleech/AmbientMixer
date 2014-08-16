#!/bin/sh

. `dirname $0`/../common.sh

if [ "$1" == "" ]; then usage "$0 <sound> - stops the specified sound"; fi

send "background_sound" "stop" $1
