import socket
import threading

PORT = 21630
HOST = "127.0.0.1"

connections = []

def handle(conn, addr):
	connected = True
	while connected:
		message = conn.recv(1024)
		for conn in connections:
			conn.send(message)
	conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        
        connections.append(conn)
        
        thread = threading.Thread(target = handle, args = (conn, addr))
        thread.start()