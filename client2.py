# import all the required modules
import socket
import threading
import time
from tkinter import *
from tkinter import font, ttk

PORT = 21630
HOST = "127.0.0.1"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# UTIL section
def util_extract_data_list(message, start_idx = 2): # idx 0 is command and idx 1 is status
    result = []
    current_idx = start_idx
    while current_idx < len(message):
        name = message[current_idx+1 : current_idx + int(message[current_idx]) + 1]
        current_idx = current_idx + int(message[current_idx]) + 1
        result.append(" ".join(name))
    return result

# GUI class for the chat
class GUI:
    # constructor method
    def __init__(self):

        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()

        # login window
        self.login = Toplevel()
        # set the title
        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=300)
        # create a Label
        self.pls = Label(self.login,
                         text="Please enter your name",
                         justify=CENTER,
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)
        # create a Label
        self.labelName = Label(self.login,
                               text="Name: ",
                               font="Helvetica 12")

        self.labelName.place(relheight=0.2,
                             relx=0.1,
                             rely=0.2)

        # create a entry box for
        # tyoing the message
        self.entryName = Entry(self.login,
                               font="Helvetica 14")

        self.entryName.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.2)

        # set the focus of the cursor
        self.entryName.focus()

        # create a Continue Button
        # along with action
        self.go = Button(self.login,
                         text="ENTER CHAT",
                         font="Helvetica 14 bold",
                         command=lambda: self.goAhead(self.entryName.get()))

        self.go.place(relx=0.4,
                      rely=0.55)
        self.Window.mainloop()

    def goAhead(self, name):
        # get the root window object
        self.login.destroy()
        self.name = name
        self.root = Tk()
        self.root.geometry("800x600")
        self.root.title("Information")

        self.user_label = Label(self.root, text=f"Hello {name}")
        self.user_label.pack(side=TOP, padx=5, pady=5)

        # create the "Available Users" listbox and its header
        self.users_frame = Frame(self.root)
        self.users_frame.pack(side=TOP, padx=5, pady=5, fill=BOTH)

        self.users_label = Label(self.users_frame, text="Available Users")
        self.users_label.pack(side=TOP, padx=5, pady=5)
        self.users_listbox = Listbox(self.users_frame)
        self.users_listbox.pack(fill=BOTH, expand=True)
        
        
        
        
        
       
        rcv2 = threading.Thread(target=self.receive_msg)
        rcv2.start()

        # create the "Available Groups" listbox and its header
        self.groups_frame = Frame(self.root)
        self.groups_frame.pack(side=TOP, padx=5, pady=5, fill=BOTH)

        self.groups_label = Label(self.groups_frame, text="Available Groups")
        self.groups_label.pack(side=TOP, padx=5, pady=5)

        self.groups_listbox = Listbox(
            self.groups_frame)
        self.groups_listbox.pack(fill=BOTH, expand=True)

        # Create a button widget to create new group
        self.create_group_button = Button(
            self.root, text="Create Group", command=self.create_group)
        self.create_group_button.pack(padx=5, pady=5, expand=True)

        self.group_name_entry = Entry(self.root)
        self.group_name_entry.pack(padx=5, pady=5, expand=True)

        self.selected_listbox = Button(
            self.root, text='talk', command=self.talk_button_clicked)
        self.selected_listbox.pack(side=BOTTOM, padx=5, pady=5, expand=True)
        self.textCons = Text(self.Window, width=20, height=2, bg="#17202A", fg="#EAECEE", font="Helvetica 14", padx=5, pady=5)

        # for tag user
        # self.users_listbox.itemconfig(0, bg="yellow")
        
        self.root.mainloop()
    
    def talk_button_clicked(self):
        if not self.users_listbox.curselection() and not self.groups_listbox.curselection():
            print("Please select listbox")
            pass
        else:
            selected_item , is_group = self.get_selected_listbox()
            if is_group :
                group_name = selected_item
                self.group_name = group_name
                self.member_list = []
                self.layout(name = group_name,member_list = self.member_list , is_group = is_group)
                self.join_group(group_name)
            elif self.name != selected_item[:len(self.name)]:
                self.member_list = sorted([selected_item,self.name])
                dm_name = f"{self.member_list[0]}_{self.member_list[1]}"
                print("dm_name_after : ",dm_name)
                self.group_name = dm_name 
                self.layout(name = dm_name,member_list = self.member_list , is_group = is_group)
                self.join_dm(dm_name,selected_item)
            else :
                print("You can't talk to yourself")
        # print("member_list : ", member_list)

              
    def layout(self, name, member_list,is_group):
        self.Window.protocol('WM_DELETE_WINDOW', lambda: self.Window.withdraw())
        
        # if is_group : member_list = self.get_group_member_list(name) 
        print("is_group : ", is_group)
        print("member_list: ", member_list)


        # Show chat window
        self.Window.deiconify()
        self.Window.title(name)
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=470, height=550, bg="#17202A")

        # Create a label for the group name
        self.labelHead = Label(self.Window, bg="#17202A", fg="#EAECEE", text=self.group_name, font="Helvetica 13 bold", pady=5)
        self.labelHead.place(relwidth=1)

        # Create a text box for displaying the chat messages
        self.textCons = Text(self.Window, width=20, height=2, bg="#17202A", fg="#EAECEE", font="Helvetica 14", padx=5, pady=5)
        self.textCons.place(relheight=0.745, relwidth=1, rely=0.08)
        self.textCons.configure(cursor="arrow", state=DISABLED)
        # Create a Scrollbar for the text box
        scrollbar = Scrollbar(self.textCons)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.configure(command=self.textCons.yview)
        

        # Create a label at the bottom for user input
        self.labelBottom = Label(self.Window, bg="#ABB2B9", height=80)
        self.labelBottom.place(relwidth=1, rely=0.825)

        # Create an entry field for typing messages
        self.entryMsg = Entry(self.labelBottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13")
        # Place the text box and the entry field on the same line
        self.entryMsg.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.entryMsg.focus()

        # Create a label to display the member list
        self.members_label = Label(self.Window, bg="#17202A", fg="#EAECEE", text=f"Members count: {len(self.member_list)}", font="Helvetica 10 bold", pady=5)
        self.members_label.place(relx=0.02, rely=0.05)

        # Create a text box to display the member list
        self.members_textbox = Text(self.Window, width=20, height=3, bg="#17202A", fg="#EAECEE", font="Helvetica 10", padx=5, pady=5)
        self.members_textbox.config(state=DISABLED)
        self.members_textbox.place(relx=0.02, rely=0.1)        

        

        # Create a Send Button
        self.buttonMsg = Button(self.labelBottom, text="Send", font="Helvetica 10 bold", width=20, bg="#ABB2B9", command=lambda: self.sendButton(self.entryMsg.get()))
        self.buttonMsg.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)
        
        # Create a button to leave the group
        
        self.leave_group_button = Button(self.labelHead, text="Leave Group", font="Helvetica 10 bold", width=10,height=1, bg="#ABB2B9", command=lambda: self.leave_group(self.group_name))
        if (not is_group) : 
            self.leave_group_button.place(
            relx=2, rely=2 )
        else :
            self.leave_group_button.place(
                    relx=0.8, rely=0.15 )

        

        
        
    def sendButton(self, msg):
        self.textCons.config(state = DISABLED)
        self.msg=msg
        self.entryMsg.delete(0, END)
        self.sendMessage()
        # snd= threading.Thread(target = self.sendMessage)
        # snd.start()
        
    def sendMessage(self):
        req = f"/message {len(self.group_name.split())} {self.group_name} {self.msg}"
        client.send(req.encode("utf-8"))
            
        
    def get_selected_listbox(self):
        """
        Returns the value of the item currently selected in the given listbox.
        """
        
        for i in self.users_listbox.curselection():
            return (self.users_listbox.get(i),0)
    
        for i in self.groups_listbox.curselection():
            return (self.groups_listbox.get(i),1) 
        
    def get_start_page(self):
        self.rename(self.name)
        message = client.recv(1024).decode("utf-8")[1:].split()
        while(message[0] == "broadcast"):
            message = client.recv(1024).decode("utf-8")[1:].split()

        self.get_group_list()
        message = client.recv(1024).decode("utf-8")[1:].split()
        while(message[0] == "broadcast"):
            message = client.recv(1024).decode("utf-8")[1:].split()
        group_list = util_extract_data_list(message, start_idx = 2)
        self.update_group_list(group_list)

        self.get_online_list()
        message = client.recv(1024).decode("utf-8")[1:].split()
        while(message[0] == "broadcast"):
            message = client.recv(1024).decode("utf-8")[1:].split()
        username_list = util_extract_data_list(message, start_idx=2)
        self.update_online_list(username_list)
    
    
    def receive_msg(self):
        self.get_start_page()
        # self.get_online_list()
        while True:
            message = client.recv(1024).decode("utf-8")
            print("received message : ",message)
            message = message[1:].split()
            match message[0] :
                case "broadcast": #todo : handle broadcast 
                    match message[1]:
                        case "online":
                            username_list = util_extract_data_list(message, start_idx=2)
                            self.update_online_list(username_list)
                        case "message":
                            # f"/broadcast message {group_name_length} {group_name} {username_length} {username} {len(message.split(' '))}" + message
                            # TODO insert received message to chat box
                            self.textCons.config(state = NORMAL)
                            extracted_data = util_extract_data_list(message, start_idx=2)
                            sender = extracted_data[1]
                            text_massage = extracted_data[2]
                            self.update_message(text_massage,sender)
                        case "group":
                            group_list = util_extract_data_list(message, start_idx = 2)
                            self.update_group_list(group_list)
                        case "join":
                            extracted_data = util_extract_data_list(message , start_idx=2)
                            self.update_group_member_list(extracted_data)
                            # TODO 
                        
                        case _:
                            print("no understandable message found")
                case "create":
                    # no response
                    pass
                case "dm":
                    # no response
                    pass
                case "join" :
                    if message[1] == "error":
                        # TODO handle "join error Group not found" message
                        
                        pass
                    else :
                        messages_list = util_extract_data_list(message)
                        # even_idx = message_context, odd_idx = message_sender
                        self.textCons.config(state=NORMAL)
                        self.textCons.insert(END, "\n\n\n\n")
                        self.textCons.config(state=DISABLED)
                        self.textCons.see(END)
                        for idx in range(0, len(messages_list), 2):
                            message_context = messages_list[idx]
                            message_sender = messages_list[idx+1]
                            # TODO display it on chat box
                            # self.textCons
                            self.update_join(message_context,message_sender)
                            
                case "leave" :
                    if message[1] == "error":
                        # TODO handle "leave error Group not found" message
                        
                        # TODO handle "leave error The user is not in this group" message
                        pass
                    else :
                        self.Window.withdraw()
                        # TODO handle "leave success"
                        pass
                case "message":
                    if message[1] == "error":
                        # TODO handle "message error Group not found" message

                        # TODO handle "message error The user is not a member or owner of the group" message
                        pass
                    else :
                        username_length = int(message[2])
                        username = message[3:3+username_length]
                        message_context = message[3+username_length:]
                        # TODO display the message on chat box
                case "rename":
                    if message[1] == "error":
                        # TODO handle "rename error The name is already taken" message
                        pass
                    else :
                        old_username_length = int(message[2])
                        old_username = message[3: 3+old_username_length]
                        new_username_length = int(message[3+old_username_length])
                        new_username = message[4+old_username_length:4+old_username_length+new_username_length]
                        # TODO handle extracted data
                case "online_list":
                    username_list = util_extract_data_list(message, start_idx=2)
                    self.update_online_list(username_list)
                case "whoami":
                    username_length = message[2]
                    username = message[3:3+username_length]
                    # TODO handel extracted data
                case "group_member":
                    if message[1] == "error":
                        # TODO handle "group_member error Group not found" message
                        pass
                    else :
                        member_list = util_extract_data_list(message, start_idx=2)
                case "group_list":
                    group_list = util_extract_data_list(message, start_idx = 2)
                    self.update_group_list(group_list)
                    
    def update_message(self, message_context, message_sender):
        self.textCons.config(state=NORMAL)
        if self.name == message_sender:
            self.textCons.tag_config('right', justify='right', rmargin=16)
            self.textCons.insert(END, f"{message_context}\n\n","right")
            # self.textCons.insert(END,"\n")
        else : 
            self.textCons.insert(END, f"{message_sender} : {message_context}\n\n")
        
        
    def create_group(self):
        self.group_name = self.group_name_entry.get()
        # Add new group to the listbox
        if len(self.group_name):
            self.groups_listbox.insert(END, self.group_name)
            # Clear the group name entry
            self.group_name_entry.delete(0, END)
            # Send the create group message to the server  
            length_group = self.group_name.split()
            client.send(f"/create {len(length_group)} {self.group_name}".encode("utf-8"))
        else :
            print("group name must be string")
    def join_group(self, group_name):
        # Send the join group message to the server
        client.send(f"/join {len(group_name.split())} {group_name}".encode("utf-8"))

    def join_dm(self, group_name,name):
        req = f"/dm {len(group_name.split())} {group_name} {len(name.split())} {name}"
        client.send(req.encode("utf-8"))

    def leave_group(self, group_name):
        self.Window.withdraw()
        client.send(f"/leave {len(group_name.split())} {group_name}".encode("utf-8"))

    def get_online_list(self):
        try:
            client.send("/online_list".encode("utf-8"))
        except:
            pass

    def update_online_list(self, username_list):
        print("online_list: ",username_list)
        self.users_listbox.delete(0,END)
        for i in  username_list :
            if i == self.name : self.users_listbox.insert(END, f"{i} (me)")
            else :self.users_listbox.insert(END, f"{i}")
        
    def get_group_list(self):
        try:
            client.send("/group_list".encode("utf-8"))
        except:
            pass

    def update_group_list(self, group_list):
        print("group_list: ",group_list)
        self.groups_listbox.delete(0,END)
        for i in group_list :
            self.groups_listbox.insert(END, f"{i}")
            
    def get_group_member_list(self,group_name):
        try:
            client.send(f"/group_member {len(group_name)} {group_name}".encode("utf-8"))
        except:
            pass

    def update_group_member_list(self, group_member):
        self.member_list = group_member
        
        self.members_textbox.configure(state=NORMAL)
        self.members_textbox.delete('1.0', END)
        print("update_group_member_list: ",group_member)
        for member in group_member:
            self.members_textbox.insert(END, member + '\n')
        self.members_textbox.configure(state=DISABLED)
        self.members_label.configure(text=f"Members count: {len(group_member)}")
        
            
    def rename(self,name):
        try:
            if len(name.strip()) > 0:
                client.send(f"/rename {len(name)} {name}".encode("utf-8"))
        except:
            pass
    def update_join(self,message_context,message_sender):
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, f"{message_sender} : {message_context}\n\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
    


# create a GUI class object
g = GUI()
