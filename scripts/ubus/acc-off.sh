#!/bin/sh

. `dirname $0`/../common.sh

if [ "$1" == "" ]; then usage "$0 <node> <event> - sends a ASOF event to the named node"; fi
if [ "$2" == "" ]; then usage "$0 <node> <event> - sends a ASOF event to the named node"; fi

ubus "ACOF" "$1" "$2"