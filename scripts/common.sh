#!/bin/sh

usage() {
	echo $1
	exit 1
}

send() {
	curl -s -X POST "http://localhost:9988/" -H "Content-Type: application/json" -d "{\"target\":\"$1\",\"method\":\"$2\",\"name\":\"$3\",\"args\":[$4]}" > /dev/null
}

