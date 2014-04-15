import sys
import socket


def send(command):
	sock = socket.socket()
	sock.connect(('localhost', 9988))
	sock.send(command)
	sock.close()


while True:
	# read input
	command = sys.stdin.readline().strip()
	
	if len(command) > 0:
		send(command)
