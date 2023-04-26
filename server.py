import socket
import selectors
import types

PORT = 21630
HOST = "127.0.0.1"

connections = []

sel = selectors.DefaultSelector()
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def accept_wrapper(sock):
	conn, addr = sock.accept()  # Should be ready to read
	print('Accepted connection from', addr)
	conn.setblocking(False)
	data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
	events = selectors.EVENT_READ | selectors.EVENT_WRITE
	connections.append(conn)
	sel.register(conn, events, data=data)

def service_connection(key, mask):
	sock = key.fileobj
	data = key.data
	if mask & selectors.EVENT_READ: # Should be ready to read
		try: 
			recv_data = sock.recv(1024)  
			if recv_data:
				data.outb += recv_data
		except:
			print('Closing connection to', data.addr)
			connections.remove(sock)
			sel.unregister(sock)
			sock.close()
	if mask & selectors.EVENT_WRITE: # Should be ready to write
		if data.outb:
			print('Echoing', repr(data.outb), 'to', data.addr)
			sent = sock.send(data.outb)  
			# broadcast to all connections
			for conn in connections:
				if conn != sock:
					conn.send(data.outb)
			data.outb = data.outb[sent:] # remove from send buffer

lsock.bind((HOST, PORT))
lsock.listen()
print('Listening on', (HOST, PORT), "...")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

while True:
    # blocks until sockets are ready, then returns (key, events) of each socket
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:  # From listener socket - we accept it
            accept_wrapper(key.fileobj)
        else: # From client socket - we service it
            service_connection(key, mask)