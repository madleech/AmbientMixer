#!/usr/bin/env bash

usage() {
	echo $1
	exit 1
}

die() {
	echo $1
	exit 1
}

send() {
	curl -s -X POST "http://localhost:9988/" -H "Content-Type: application/json" -d "{\"target\":\"$1\",\"method\":\"$2\",\"name\":\"$3\",\"args\":[$4]}" > /dev/null
}

get() {
	curl -s -X POST "http://localhost:9988/" -H "Content-Type: application/json" -d "{\"target\":\"$1\",\"method\":\"$2\",\"name\":\"$3\",\"args\":[$4]}"
}

upload() {
	if [ ! -f "$1" ]; then die "Could not find file $1"; fi
	curl -s -X POST "http://localhost:9988/" -F file=@"$1" -F json="{\"target\":\"$2\",\"method\":\"$3\",\"name\":\"$4\",\"args\":[$5]}" # > /dev/null
}

ubus() {
	cd `dirname $0`/../../
	python send_ubus_packet.py "$1" "$2" "$3"
}
