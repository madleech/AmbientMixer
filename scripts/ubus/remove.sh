#!/bin/sh

. `dirname $0`/../common.sh

if [ "$1" == "" ]; then usage "$0 <node> <event> - removes selected UBUS mapping"; fi
if [ "$2" == "" ]; then usage "$0 <node> <event> - removes selected UBUS mapping"; fi

send "ubus" "remove_mapping" "", "{\"node\":$1, \"event\":$2}"
