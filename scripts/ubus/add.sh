#!/usr/bin/env bash

. `dirname $0`/../common.sh

if [ "$1" == "" ]; then usage "$0 <node> <event> <sound> - adds a new UBUS mapping for the given node and event"; fi
if [ "$2" == "" ]; then usage "$0 <node> <event> <sound> - adds a new UBUS mapping for the given node and event"; fi
if [ "$3" == "" ]; then usage "$0 <node> <event> <sound> - adds a new UBUS mapping for the given node and event"; fi

send "ubus" "update_mapping" "", "{\"node\":$1, \"event\":$2, \"sound\":\"$3\"}"
