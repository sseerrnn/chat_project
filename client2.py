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
    print("message util: ",message )
    while current_idx < len(message):
        name = message[current_idx+1 : current_idx + int(message[current_idx]) + 1]
        current_idx = current_idx + int(message[current_idx]) + 1
        result.append(" ".join(name))
    print("result", result)
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

        # rcv3 = threading.Thread(target=self.get_group_list)
        # rcv3.start()
        
        # for i in rcv2:
        #     self.users_listbox.insert(END, f"User {i}")

        # create the "Available Groups" listbox and its header
        self.groups_frame = Frame(self.root)
        self.groups_frame.pack(side=TOP, padx=5, pady=5, fill=BOTH)

        self.groups_label = Label(self.groups_frame, text="Available Groups")
        self.groups_label.pack(side=TOP, padx=5, pady=5)

        self.groups_listbox = Listbox(
            self.groups_frame)
        self.groups_listbox.pack(fill=BOTH, expand=True)

        # for i in range(20):
        #     self.groups_listbox.insert(END, f"Group {i}")

        # Create a button widget to create new group
        self.create_group_button = Button(
            self.root, text="Create Group", command=self.create_group)
        self.create_group_button.pack(padx=5, pady=5, expand=True)

        self.group_name_entry = Entry(self.root)
        self.group_name_entry.pack(padx=5, pady=5, expand=True)

        self.selected_listbox = Button(
            self.root, text='talk', command=self.talk_button_clicked)
        self.selected_listbox.pack(side=BOTTOM, padx=5, pady=5, expand=True)

        # for tag user
        # self.users_listbox.itemconfig(0, bg="yellow")
        self.root.mainloop()
    
    def talk_button_clicked(self):
        selected_item , is_group = self.get_selected_listbox()
        print(selected_item , " " , is_group)
        member_list = []
        if is_group :
            name = selected_item
            member_list = []
        else :
            name = f"{selected_item} And {self.name}"  
            if selected_item < self.name :
                member_list = [selected_item , self.name]
            else :
                member_list = [self.name , selected_item]
        # print("member_list : ", member_list)
        self.layout(name = name,member_list = member_list , is_group = is_group)
              
    def layout(self, name, member_list,is_group):
        self.Window.protocol('WM_DELETE_WINDOW', lambda: self.Window.withdraw())
        # if is_group : member_list = self.get_group_member_list(name) 
        print("is_group : ", is_group)
        print("member_list: ", member_list)
        self.name = name

        # Show chat window
        self.Window.deiconify()
        self.Window.title(name)
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=470, height=550, bg="#17202A")

        # Create a label for the group name
        self.labelHead = Label(self.Window, bg="#17202A", fg="#EAECEE", text=self.name, font="Helvetica 13 bold", pady=5)
        self.labelHead.place(relwidth=1)

        # Create a text box for displaying the chat messages
        self.textCons = Text(self.Window, width=20, height=2, bg="#17202A", fg="#EAECEE", font="Helvetica 14", padx=5, pady=5)
        self.textCons.place(relheight=0.745, relwidth=1, rely=0.08)

        # Create a label at the bottom for user input
        self.labelBottom = Label(self.Window, bg="#ABB2B9", height=80)
        self.labelBottom.place(relwidth=1, rely=0.825)

        # Create an entry field for typing messages
        self.entryMsg = Entry(self.labelBottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13")

        # Create a label to display the member list
        members_label = Label(self.Window, bg="#17202A", fg="#EAECEE", text=f"Members count: {len(member_list)}", font="Helvetica 10 bold", pady=5)
        members_label.place(relx=0.02, rely=0.05)

        # Create a text box to display the member list
        members_textbox = Text(self.Window, width=20, height=3, bg="#17202A", fg="#EAECEE", font="Helvetica 10", padx=5, pady=5)
        members_textbox.place(relx=0.02, rely=0.1)

        

        # Insert member names into the text box
        for member in member_list:
            members_textbox.insert(END, member + '\n')

        # Create a Send Button
        self.buttonMsg = Button(self.labelBottom, text="Send", font="Helvetica 10 bold", width=20, bg="#ABB2B9", command=lambda: self.sendButton(self.entryMsg.get()))
        self.buttonMsg.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)
        
        # Create a button to leave the group
        self.leave_group_button = Button(self.Window, text="Leave Group", font="Helvetica 10 bold", width=20, bg="#ABB2B9", command=lambda: self.leave_group())
        
        
    def sendButton(self, msg):
        self.textCons.config(state = DISABLED)
        self.msg=msg
        self.entryMsg.delete(0, END)
        snd= threading.Thread(target = self.sendMessage)
        snd.start()
        
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
        # username_list = util_extract_data_list(message, start_idx=2)
        
        self.get_online_list()
        message = client.recv(1024).decode("utf-8")[1:].split()
        username_list = util_extract_data_list(message, start_idx=2)
        self.update_online_list(username_list)
        self.get_group_list()
        message = client.recv(1024).decode("utf-8")[1:].split()
        group_list = util_extract_data_list(message, start_idx = 2)
        self.update_group_list(group_list)
    
    
    def receive_msg(self):
        self.get_start_page()
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
                        case "massage":
                            client.send("/")
                        case "group":
                            group_list = util_extract_data_list(message, start_idx = 2)
                            self.update_group_list(group_list)
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
                        for idx in range(0, len(messages_list), 2):
                            message_context = messages_list[idx]
                            message_sender = messages_list[idx+1]
                            # TODO display it on chat box
                            
                case "leave" :
                    if message[1] == "error":
                        # TODO handle "leave error Group not found" message
                        
                        # TODO handle "leave error The user is not in this group" message
                        pass
                    else :
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
                        print(member_list)
                case "group_list":
                    group_list = util_extract_data_list(message, start_idx = 2)
                    self.update_group_list(group_list)
                    

    def create_group(self):
        group_name = self.group_name_entry.get()
        # Add new group to the listbox
        self.groups_listbox.insert(END, group_name)
        # Clear the group name entry
        self.group_name_entry.delete(0, END)
        # Send the create group message to the server
        client.send(f"/create {len(group_name)} {group_name}".encode("utf-8"))

    def get_online_list(self):
        try:
            client.send("/online_list".encode("utf-8"))
            time.sleep(2)
            
        except:
            pass

    def update_online_list(self, username_list):
        print("online_list: ",username_list)
        self.users_listbox.delete(0,END)
        for i in  username_list :
            if i == self.name : self.users_listbox.insert(END, f"User :{i} (me)")
            else :self.users_listbox.insert(END, f"User :{i}")
        

    def get_group_list(self):
            try:
                client.send("/group_list".encode("utf-8"))
                
            except:
                pass

    def update_group_list(self, group_list):
        print("group_list: ",group_list)
        self.groups_listbox.delete(0,END)
        for i in  group_list :
            self.groups_listbox.insert(END, f"group :{i}")
            
    def get_group_member_list(self,group_name):
        try:
            client.send(f"/member_list {len(group_name)} {group_name}".encode("utf-8"))
        except:
            pass

    def update_group_member_list(self, message):
        pass
            
    def rename(self,name):
        try:
            if len(name.strip()) > 0:
                client.send(f"/rename {len(name)} {name}".encode("utf-8"))
                # response = client.recv(1024).decode("utf-8")
                # print("rename to : "+response.split(" ")[3])
                # print("rename response: ",response)
                # break
                # return response.split(" ")[3]
        except:
            pass

    def sendMessage(self):
        self.textCons.config(state=DISABLED)
        while True:
            message = f"{self.msg}"
            client.send(message.encode("utf-8"))
            break       
# create a GUI class object
g = GUI()
