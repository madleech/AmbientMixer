net = require 'net'
dgram = require 'dgram'

sockets = []
speaker = null # who was the last to talk

tcp_server = net.createServer (sock) ->
	console.log "tcp connected: #{sock.remoteAddress}:#{sock.remotePort}"
	sockets.push sock
	sock.on 'data', (data) ->
		speaker = sock
		console.log "<- tcp: #{to_str data} (#{sock.remoteAddress}:#{sock.remotePort})"
		udp_broadcast data
	sock.on 'end', ->
		i = sockets.indexOf sock
		sockets.splice i, 1 if i isnt -1
tcp_server.on 'error', (err) ->
	console.log "tcp error: #{err.stack}"
	tcp_server.close()

tcp_server.listen 5550, '127.0.0.1'

udp_server = dgram.createSocket 'udp4'
udp_server.on 'message', (data, client) ->
	console.log "<- udp: #{to_str data} (#{client.address}:#{client.port})"
	tcp_transmit data
udp_server.on 'error', (err) ->
	console.log "udp error: #{err.stack}"
	udp_server.close()

udp_server.bind 5550


udp_broadcast = (data) ->
	console.log "-> udp: #{to_str data}"
	data = new Buffer data
	client = dgram.createSocket 'udp4'
	client.bind()
	client.on 'listening', ->
		client.setBroadcast true
		client.send data, 0, data.length, 5550, '255.255.255.255', (err, bytes) ->
		  client.close()

tcp_transmit = (data) ->
	for sock in sockets
		if speaker isnt sock
			console.log "-> tcp: #{to_str data} (#{sock.remoteAddress}:#{sock.remotePort})"
			sock.write data
	speaker = null

to_str = (buffer) ->
	"#{buffer}".trim()
