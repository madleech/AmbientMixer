#!/bin/bash

. `dirname $0`/../common.sh

if [ "$1" == "" ]; then usage "$0 <node> <event> - sends a ASON event to the named node"; fi
if [ "$2" == "" ]; then usage "$0 <node> <event> - sends a ASON event to the named node"; fi

ubus "ACON" "$1" "$2"
