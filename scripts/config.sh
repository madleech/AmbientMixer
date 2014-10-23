#!/usr/bin/env bash

. `dirname $0`/common.sh

echo "SOUNDS"
get "sequencer" "get_config"

echo "\n\nUBUS"
get "ubus" "get_config"
