import selectors
import socket
import types
from datetime import datetime

PORT = 21630
HOST = "127.0.0.1"

connections = []
user_id = 1
sel = selectors.DefaultSelector()
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
groups = []
users = dict()
id2name = dict()

def accept_wrapper(sock):
	conn, addr = sock.accept()  # Should be ready to read
	print('Accepted connection from', addr)
	conn.setblocking(False)
	data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
	events = selectors.EVENT_READ | selectors.EVENT_WRITE
	connections.append(conn)
	sel.register(conn, events, data=data)
	global user_id
	
	users[conn] = {"id": user_id, "name": "default"}
	id2name[user_id] = "default"
	user_id += 1

	# broadcast to all user
	for conn_t in connections:
		if(conn == conn_t): continue
		conn_t.send(b'/broadcast online')


def service_connection(key, mask):
	sock = key.fileobj
	data = key.data
	if mask & selectors.EVENT_READ: # Should be ready to read
		try: 
			recv_data = sock.recv(1024).decode()
			'''
			Receive Protocol : 
				/create [len of group_name] [group_name]
				/join [len of group_name] [group_name]
				/leave [len of group_name] [group_name]
				/exit
				/messsage [len of group_name] [group_name] [message]
				/whoami	
				/rename [len of new_name] [new_name]
				
				/group_list
				/group_member [len of group_name] [group_name]
				/online_list 
				

			Send Protocol :
				/[function name] error [res]
				/[function name] success [res]		

			Broadcast :
				/broadcast online => update online users list
				/broadcast message [group_name_length] [group_name] [sender_name_lenght] [sender_name] [message_context] => update message in group
				/broadcast group => update groups list
			'''
			if(recv_data[0] == '/'):
				command = recv_data[1:].split(" ")

				if(command[0] == 'create' or command[0] == 'dm'):
					group_name_length = int(command[1])
					group_name = " ".join(command[2:2+group_name_length]).strip()
					'''
					group = {
						name: string
						owner : id
						members : id[]
						messages : [{context: string, date: date, sender: id}]
						public : boolean
					}
					
					'''
					public = True
					if(command[0] == 'dm') : public = False

					group = {
						"name": group_name,
						"owner": users.get(sock).get("id"),
						"members": [users.get(sock).get("id")],
						"messages": [],
						"public": public
					}
					groups.append(group)

				elif(command[0] == 'join'):
					group_name_length = int(command[1])
					group_name = " ".join(command[2:2+group_name_length]).strip()
					group = list(filter(lambda group: group.get("name") == group_name, groups))
					if(len(group) == 0):
						# Handle group not found
						recv_data = "/join error Group not found"
					else :
						group_index = groups.index(group[0])
						if(group[0].get("owner") != users.get(sock).get("id") and  users.get(sock).get("id") not in group[0].get("members")) :
							groups[group_index].get("members").append(users.get(sock).get("id"))
						all_messages = ""
						for message in groups[group_index].get("messages"):
							context = message.get("context").strip()
							username = id2name.get(message.get("sender").strip())
							username_length = len(username.split(" "))
							context_length = len(context.split(" "))
							all_messages += f" {context_length} {context} {username_length} {username}"
						recv_data = "/join success" + " " + all_messages

				elif(command[0] == 'leave'):
					group_name_length = int(command[1])
					group_name = " ".join(command[2:2+group_name_length]).strip()
					group = list(filter(lambda group: group.get("name") == group_name, groups))
					if(len(group) == 0):
						# Handle group not found
						recv_data = "/leave error Group not found"
					elif(users.get(sock).get("id") not in group[0].get("members")):
						recv_data = "/leave error The user is not in this group"
					else :
						group_index = groups.index(group[0])
						if groups[group_index].get("owner") == users.get(sock).get("id"):
							groups.remove(group[0])
							recv_data = "/leave success"
							# TODO broadcast to close group chat window
						else:
							groups[group_index].get("members").remove(users.get(sock).get("id"))
							recv_data = "/leave success"
							# TODO broadcast to update group member
						
					

				# elif(command[0] == 'exit'):
				# 	user_id = users.get(sock).get("id")
				# 	group_list = list(filter(lambda group:  user_id in group.get("members") or user_id == group.get("owner") , groups))
				# 	for group in group_list :
				# 		group_index = groups.index(group)
				# 		if groups[group_index].get("owner") == user_id:
				# 			groups.remove(group)
				# 		else :
				# 			groups[group_index].get("members").remove(user_id)
				# 	if(user_id in id2name):
				# 		del id2name[user_id]
				# 	connections.remove(sock)
					# for conn in connections:
					# 	conn.send(b'/broadcast online')
				# 	del users[sock]
				# 	sel.unregister(sock)
				# 	sock.close()

				elif(command[0] == 'message'):
					user_id = users.get(sock).get("id")
					username = users.get(sock).get("name").strip()
					username_length = len(username.split(" "))
					group_name_length = int(command[1])
					group_name = " ".join(command[2:2+group_name_length]).strip()
					message = " ".join(command[2+group_name_length:]).strip()
					group = list(filter(lambda group: group.get("name") == group_name, groups))
					if(len(group) == 0):
						# Handle group not found
						recv_data = "/message error Group not found"
					elif(group[0].get("owner") != users.get(sock).get("id") and users.get(sock).get("id") not in group[0].get("members")):
						# Handle owner join own group
						recv_data = "/message error The user is not a member or owner of the group"
					else :
						group_index = groups.index(group[0])
						groups[group_index].get("messages").append({"context": message, "date": datetime.now(), "sender": user_id})
						recv_data = f"/message success {username_length} {username} " + message
						group_conns = groups[group_index].get("members") + [groups[group_index].get("owner")]
						# Change user_id to conn
						id2conn = {value.get("id"):key for (key,value) in users.items()}
						group_conns = [id2conn.get(id) for id in group_conns]
						for conn in group_conns:
							if(sock == conn): continue
							conn.send((f"/broadcast message {group_name_length} {group_name} {username_length} {username} " + message).encode())

					
				elif(command[0] == 'whoami'):
					name = users.get(sock).get('name').strip()
					name_length = len(name.split(" "))
					recv_data = f"/whoami success {name_length} {name}"

				
				elif(command[0] == 'group_list'):
					all_group_name = ""
					for group in groups:
						if(group.get("public") == False) : continue
						group_name = group.get("name").strip()
						group_name_length = len(group_name.split(" "))
						all_group_name += f" {group_name_length} {group_name}"
					recv_data = "/group_list success" + all_group_name        

				elif(command[0] == 'group_member'):
					group_name_length = int(command[1])
					group_name = " ".join(command[2:2+group_name_length]).strip()
					group = list(filter(lambda group: group.get("name") == group_name, groups))
					if(len(group) == 0):
						# Handle group not found
						recv_data = "/group_member error Group not found"
					else :
						group_index = groups.index(group[0])
						all_messages = ""
						for member in groups[group_index].get("members"):
							mem_name = id2name.get(member).strip()
							mem_name_length = len(mem_name.split(" "))
							all_messages += f" {mem_name_length} {mem_name}"
						recv_data = "/group_member success" + all_messages
                        
                
				elif(command[0] == 'online_list'):
					online = ""
					for conn in connections:
						# if(sock == conn): continue
						name = users.get(conn).get("name").strip()
						name_length = len(name.split(" "))
						online += f" {name_length} {name}"
					recv_data = "/online_list success" + online

				elif(command[0] == 'rename'):
					user_id = users.get(sock).get("id")
					username = users.get(sock).get("name").strip()
					username_length = len(username.split(" "))
					new_name_length = int(command[1])
					new_name = " ".join(command[2:2+new_name_length]).strip()
					if(new_name in id2name.values()):
						recv_data = "/rename error The name is already taken"
					else :
						users[sock]["name"] = new_name
						id2name[user_id] = new_name
						print(users)
						recv_data = "/rename success " +str(username_length)+" "+username+ " "+str(new_name_length)+" "+new_name
						
						for conn in connections:
							if(sock == conn): continue
							# conn.send((f"/broadcast online {username_length} {username} {new_name_length} {new_name}").encode())
							conn.send((f"/broadcast online").encode())

			if recv_data:
				data.outb += recv_data.encode()
		except Exception as e:
			print(e)
			print('Closing connection to', data.addr)
			user_id = users.get(sock).get("id")
			group_list = list(filter(lambda group:  user_id in group.get("members") or user_id == group.get("owner") , groups))
			for group in group_list :
				group_index = groups.index(group)
				if groups[group_index].get("owner") == user_id:
					groups.remove(group)
				else :
					groups[group_index].get("members").remove(user_id)
			if(user_id in id2name):
				del id2name[user_id]
			connections.remove(sock)
			del users[sock]
			sel.unregister(sock)
			sock.close()
			for conn in connections:
				conn.send(b'/broadcast online')

	if mask & selectors.EVENT_WRITE: # Should be ready to write
		if data.outb:
			print('Echoing', repr(data.outb), 'to', data.addr)
			sent = sock.send(data.outb)  
			# broadcast to all connections
			# for conn in connections:
			# 	if conn != sock:
			# 		conn.send(data.outb)
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