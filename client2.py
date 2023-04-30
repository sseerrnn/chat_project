# import all the required modules
import socket
import threading
from tkinter import *
from tkinter import font
from tkinter import ttk

PORT = 21630
HOST = "127.0.0.1"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

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

        rcv1 = threading.Thread(target=self.rename(self.entryName.get()))
        rcv1.start()
        
        rcv2 = threading.Thread(target=self.get_online_list)
        rcv2.start()

        for i in range(5):
            self.users_listbox.insert(END, f"User {i}")

        # create the "Available Groups" listbox and its header
        self.groups_frame = Frame(self.root)
        self.groups_frame.pack(side=TOP, padx=5, pady=5, fill=BOTH)

        self.groups_label = Label(self.groups_frame, text="Available Groups")
        self.groups_label.pack(side=TOP, padx=5, pady=5)

        self.groups_listbox = Listbox(
            self.groups_frame)
        self.groups_listbox.pack(fill=BOTH, expand=True)

        for i in range(20):
            self.groups_listbox.insert(END, f"Group {i}")

        # Create a button widget to create new group
        self.create_group_button = Button(
            self.root, text="Create Group", command=self.create_group)
        self.create_group_button.pack(padx=5, pady=5, expand=True)

        self.group_name_entry = Entry(self.root)
        self.group_name_entry.pack(padx=5, pady=5, expand=True)

        self.selected_listbox = Button(
            self.root, text='talk', command=lambda: print(self.get_selected_listbox()))
        self.selected_listbox.pack(side=BOTTOM, padx=5, pady=5, expand=True)

        # for tag user
        # self.users_listbox.itemconfig(0, bg="yellow")
        self.root.mainloop()

    def get_selected_listbox(self):
        """
        Returns the value of the item currently selected in the given listbox.
        """
        for i in self.users_listbox.curselection():
            return self.users_listbox.get(i)
        for i in self.groups_listbox.curselection():
            return self.groups_listbox.get(i)

    def create_group(self):
        group_name = self.group_name_entry.get()
        # Add new group to the listbox
        self.groups_listbox.insert(END, group_name)
        # Clear the group name entry
        self.group_name_entry.delete(0, END)

    def get_online_list(self):
        while True:
            try:
                client.send("/online_list".encode("utf-8"))
                online_list = client.recv(1024).decode("utf-8")
                print("here")
                print(online_list)
                return online_list
            except:
                break

    def rename(self,name):
        while True :
            try:     
                client.send(f"/rename {len(name)} {name}".encode("utf-8"))
                response = client.recv(1024).decode("utf-8")
                print("rename to : "+response.split(" ")[3])
            except:
                break
                
# create a GUI class object
g = GUI()
