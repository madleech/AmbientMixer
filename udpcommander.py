import sys
import socket


def send(command):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.sendto(command, ('255.255.255.255', 5550))
	sock.close()


while True:
	# read input
	command = sys.stdin.readline().strip()
	
	if len(command) > 0:
		send(command)
