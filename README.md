# AmbientMixer

Loosely based on the https://www.ambient-mixer.com/ website, but extensively modified to suit my own needs.

## Installation

Set up a venv:
```
$ python3 -m venv venv
$ source venv/bin/activate.fish
```

Install requirements:
```
$ python3 -m pip install pygame
```

## Running

```
$ python3 main.py
```

You can now connect to the web UI at http://localhost:9988/

## Services

* HTTP server on port 9988, used to serve web UI.
* JSON API on port 9988.
* UBUS UDP server listening on port 5550, and broadcasting to UDP port 5550 on the local broadcast network.
* Connects to RocRail on localhost port 8051, and listens for function change events and block occupancy change events.
