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
queue = dict()
def accept_wrapper(sock):
	conn, addr = sock.accept()  # Should be ready to read
	print('Accepted connection from', addr)
	conn.setblocking(False)
	data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
	events = selectors.EVENT_READ | selectors.EVENT_WRITE
	connections.append(conn)
	sel.register(conn, events, data=data)
	global user_id
	
	users[conn] = {"id": user_id, "name": str(user_id)}
	queue[conn] = []
	id2name[user_id] = str(user_id)
	user_id += 1

	# # broadcast to all user
	# online = ""
	# for conn in connections:
	# # if(sock == conn): continue
	# 	name = users.get(conn).get("name").strip()
	# 	name_length = len(name.split(" "))
	# 	online += f" {name_length} {name}"

	# for conn in connections:
	# 	if(sock == conn): continue
	# 	conn.send((f"/broadcast online {online}").encode())


def service_connection(key, mask):
	sock = key.fileobj
	data = key.data
	if mask & selectors.EVENT_READ: # Should be ready to read
		try: 
			'''
			Receive Protocol : 
				/create [len of group_name] [group_name]
				/join [len of group_name] [group_name]
				/leave [len of group_name] [group_name]
				/dm [len of group_name] [group_name] [len of receiver username] [receiver username]
				/exit
				/message [len of group_name] [group_name] [message]
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
			if(len(queue[sock]) == 0):
				recv_data = sock.recv(1024).decode()
				if(recv_data[0] == '/'):
					command = recv_data[1:].split(" ")

					if(command[0] == 'create'):
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
						group = {
							"name": group_name,
							"owner": str(users.get(sock).get("id")),
							"members": [str(users.get(sock).get("id"))],
							# mock msg
							"messages": [{"context": group_name + " group chat is created.", "date": datetime.now(), "sender": str(users.get(sock).get("id"))}],
							"public": True
						}
						groups.append(group)

						# broadcast to all user
						all_group_name = ""
						for group in groups:
							if(group.get("public") == False) : continue
							group_name = group.get("name").strip()
							group_name_length = len(group_name.split(" "))
							all_group_name += f" {group_name_length} {group_name}"
						for conn in connections:
							if(conn == sock) : continue
							conn.send(f'/broadcast group {all_group_name}'.encode())

					elif(command[0] == 'dm'):
						print(command)
						group_name_length = int(command[1])
						group_name = " ".join(command[2:2+group_name_length]).strip()
						receiver_name_length = int(command[2+group_name_length])
						receiver_name = " ".join(command[3+group_name_length:3+group_name_length+receiver_name_length])
						print("Yess")
						group = list(filter(lambda group: group.get("name") == group_name, groups))
						if(len(group)==0):
							# find id by name
							receiver_id = ""
							for key, value in id2name.items():
								if(value == receiver_name):
									receiver_id = str(key)
							new_group = {
								"name": group_name,
								"owner": str(users.get(sock).get("id")),
								"members": [str(users.get(sock).get("id")), receiver_id],
								# mock msg
								"messages": [{"context": group_name + " direct chat is created.", "date": datetime.now(), "sender": str(users.get(sock).get("id"))}],
								"public": False
							}
							print("new",new_group)
							groups.append(new_group)
							group.append(new_group)
						group_index = groups.index(group[0])
						all_messages = ""
						for message in groups[group_index].get("messages"):
							context = message.get("context").strip()
							username = id2name.get(message.get("sender").strip())
							username_length = len(username.split(" "))
							context_length = len(context.split(" "))
							all_messages += f" {context_length} {context} {username_length} {username}"
						print("/join success" + " " + all_messages)
						queue[sock].append("/join success" + " " + all_messages)	
						

					elif(command[0] == 'join'):
						group_name_length = int(command[1])
						group_name = " ".join(command[2:2+group_name_length]).strip()
						group = list(filter(lambda group: group.get("name") == group_name, groups))
						if(len(group) == 0):
							# Handle group not found
							# recv_data = "/join error Group not found"
							queue[sock].append("/join error Group not found")
						else :
							group_index = groups.index(group[0])
							if(group[0].get("owner") != str(users.get(sock).get("id")) and  str(users.get(sock).get("id")) not in group[0].get("members")) :
								groups[group_index].get("members").append(str(users.get(sock).get("id")))
							all_messages = ""
							for message in groups[group_index].get("messages"):
								context = message.get("context").strip()
								username = id2name.get(message.get("sender").strip())
								username_length = len(username.split(" "))
								context_length = len(context.split(" "))
								all_messages += f" {context_length} {context} {username_length} {username}"
							# recv_data = "/join success" + " " + all_messages
							queue[sock].append("/join success" + " " + all_messages)
							# get all group member
							all_messages = ""
							for member in groups[group_index].get("members"):
								mem_name = id2name.get(member).strip()
								mem_name_length = len(mem_name.split(" "))
								all_messages += f" {mem_name_length} {mem_name}"
							# broadcast to group member
							queue[sock].append(f'/broadcast join {all_messages}')
							group_conns = groups[group_index].get("members")
							# Change user_id to conn
							id2conn = {str(value.get("id")):key for (key,value) in users.items()}
							group_conns = [id2conn.get(str(id)) for id in group_conns]
							for conn in group_conns:
								if(conn == sock) : continue
								conn.send(f'/broadcast join {all_messages}'.encode())
							

					elif(command[0] == 'leave'):
						group_name_length = int(command[1])
						group_name = " ".join(command[2:2+group_name_length]).strip()
						group = list(filter(lambda group: group.get("name") == group_name, groups))
						if(len(group) == 0):
							# Handle group not found
							# recv_data = "/leave error Group not found"
							queue[sock].append("/leave error Group not found")
						elif(str(users.get(sock).get("id")) not in group[0].get("members")):
							# recv_data = "/leave error The user is not in this group"
							queue.append("/leave error The user is not in this group")
						else :
							group_index = groups.index(group[0])
							groups[group_index].get("members").remove(str(users.get(sock).get("id")))
							if len(groups[group_index].get("members")) == 0:
								groups.remove(group[0])
								# broadcast to all user
								all_group_name = ""
								for group in groups:
									if(group.get("public") == False) : continue
									group_name = group.get("name").strip()
									group_name_length = len(group_name.split(" "))
									all_group_name += f" {group_name_length} {group_name}"
								for conn in connections:
									# if(conn == sock) : continue
									conn.send(f'/broadcast group {all_group_name}'.encode())
							else:
								# get all group member
								all_messages = ""
								for member in groups[group_index].get("members"):
									mem_name = id2name.get(member).strip()
									mem_name_length = len(mem_name.split(" "))
									all_messages += f" {mem_name_length} {mem_name}"
								# broadcast to group member
								group_conns = groups[group_index].get("members")
								# Change user_id to conn
								id2conn = {str(value.get("id")):key for (key,value) in users.items()}
								group_conns = [id2conn.get(str(id)) for id in group_conns]
								for conn in group_conns:
									if(conn == sock) : continue
									conn.send(f'/broadcast join {all_messages}'.encode())
							queue[sock].append("/leave success")
							
						
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
						user_id = str(users.get(sock).get("id"))
						username = users.get(sock).get("name").strip()
						username_length = len(username.split(" "))
						group_name_length = int(command[1])
						group_name = " ".join(command[2:2+group_name_length]).strip()
						message = " ".join(command[2+group_name_length:]).strip()
						group = list(filter(lambda group: group.get("name") == group_name, groups))
						if(len(group) == 0):
							# Handle group not found
							# recv_data = "/message error Group not found"
							queue[sock].append("/message error Group not found")
						elif(group[0].get("owner") != str(users.get(sock).get("id")) and str(users.get(sock).get("id")) not in group[0].get("members")):
							# Handle owner join own group
							# recv_data = "/message error The user is not a member or owner of the group"
							queue[sock].append("/message error The user is not a member or owner of the group")
						else :
							group_index = groups.index(group[0])
							groups[group_index].get("messages").append({"context": message, "date": datetime.now(), "sender": user_id})
							# recv_data = f"/message success {username_length} {username} " + message
							queue[sock].append(f"/broadcast message {group_name_length} {group_name} {username_length} {username} {len(message.split(' '))} {message}")
							group_conns = groups[group_index].get("members")
							# Change user_id to conn
							id2conn = {str(value.get("id")):key for (key,value) in users.items()}
							group_conns = [id2conn.get(str(id)) for id in group_conns]
							for conn in group_conns:
								if(sock == conn): continue
								conn.send((f"/broadcast message {group_name_length} {group_name} {username_length} {username} {len(message.split(' '))} {message}").encode())

						
					elif(command[0] == 'whoami'):
						name = users.get(sock).get('name').strip()
						name_length = len(name.split(" "))
						# recv_data = f"/whoami success {name_length} {name}"
						queue[sock].append(f"/whoami success {name_length} {name}")

					
					elif(command[0] == 'group_list'):
						all_group_name = ""
						for group in groups:
							if(group.get("public") == False) : continue
							group_name = group.get("name").strip()
							group_name_length = len(group_name.split(" "))
							all_group_name += f" {group_name_length} {group_name}"
						# recv_data = "/group_list success" + all_group_name    
						queue[sock].append("/group_list success" + all_group_name )    

					elif(command[0] == 'group_member'):
						group_name_length = int(command[1])
						group_name = " ".join(command[2:2+group_name_length]).strip()
						group = list(filter(lambda group: group.get("name") == group_name, groups))
						if(len(group) == 0):
							# Handle group not found
							# recv_data = "/group_member error Group not found"
							queue[sock].append("/group_member error Group not found")
						else :
							group_index = groups.index(group[0])
							all_messages = ""
							for member in groups[group_index].get("members"):
								mem_name = id2name.get(member).strip()
								mem_name_length = len(mem_name.split(" "))
								all_messages += f" {mem_name_length} {mem_name}"
							# recv_data = "/group_member success" + all_messages
							queue[sock].append("/group_member success" + all_messages)
							
					
					elif(command[0] == 'online_list'):
						online = ""
						for conn in connections:
							# if(sock == conn): continue
							name = users.get(conn).get("name").strip()
							name_length = len(name.split(" "))
							online += f" {name_length} {name}"
						# recv_data = "/online_list success" + online
						queue[sock].append("/online_list success" + online)

					elif(command[0] == 'rename'):
						user_id = str(users.get(sock).get("id"))
						username = users.get(sock).get("name").strip()
						username_length = len(username.split(" "))
						new_name_length = int(command[1])
						new_name = " ".join(command[2:2+new_name_length]).strip()
						if(new_name in id2name.values()):
							# recv_data = "/rename error The name is already taken"
							queue[sock].append("/rename error The name is already taken")
						else :
							users[sock]["name"] = new_name
							id2name[user_id] = new_name
							# recv_data = "/rename success " +str(username_length)+" "+username+ " "+str(new_name_length)+" "+new_name
							queue[sock].append("/rename success " +str(username_length)+" "+username+ " "+str(new_name_length)+" "+new_name)
							online = ""
							for conn in connections:
							# if(sock == conn): continue
								name = users.get(conn).get("name").strip()
								name_length = len(name.split(" "))
								online += f" {name_length} {name}"

							# queue[sock].append(f"/broadcast online {online}");
							for conn in connections:
								if(sock == conn): continue
								conn.send((f"/broadcast online {online}").encode())
					else :
						exit()
			if len(queue[sock]) > 0:
				data_t = queue[sock].pop(0)
				data.outb += data_t.encode()
		except Exception as e:
			print(e)
			print('Closing connection to', data.addr)
			user_id = str(users.get(sock).get("id"))
			group_list = list(filter(lambda group:  user_id in group.get("members") or user_id == group.get("owner") , groups))
			for group in group_list :
				group_index = groups.index(group)
				if groups[group_index].get("owner") == user_id:
					groups.remove(group)
				else :
					groups[group_index].get("members").remove(user_id)
			online = ""
			for conn in connections:
				if(sock == conn): continue
				name = users.get(conn).get("name").strip()
				name_length = len(name.split(" "))
				online += f" {name_length} {name}"
			if(user_id in id2name):
				del id2name[user_id]
			connections.remove(sock)
			del users[sock]
			sel.unregister(sock)
			sock.close()

	if mask & selectors.EVENT_WRITE: # Should be ready to write
		if data.outb or len(queue[sock]) > 0:
			if(not data.outb and len(queue[sock]) > 0):
				data.outb += (queue[sock].pop(0)).encode()
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