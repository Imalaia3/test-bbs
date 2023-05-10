import socket
import json
from colorama import Fore
with open("config.json") as f:
    CONFIG = json.loads(f.read())
    f.close()

class User:
    #might move to utils.py
    def userinput(self,msg:str):
        self.sock.send(msg.encode("utf-8"))
        data = self.sock.recv(2048)
        if not data:
           return None
        return data
    
    def userprint(self,msg:str):
        self.sock.send(msg.encode("utf-8"))




    def clear(self):
        self.sock.send("\033[2J\033[H".encode("utf-8"))
        self.sock.send(CONFIG["splash"].encode("utf-8"))


    def read_messages(self):
        self.clear()
        self.userprint("All Messages:\n")
        with open("messages.json") as msgf:
            msgs = json.loads(msgf.read())
            msgf.close()

        output = ""
        for c,message in enumerate(msgs["messages"]):
            author  = message[0]
            title   = message[1]
            #content = message[2]
            output += f"({c})[{author}] {title}\n"


        self.userprint(output)
        while True:
            choice = self.userinput("\nSelect a message: ")
            choice = choice[0:len(choice)-2].decode("utf-8")
            try:
                if int(choice) > len(msgs["messages"])-1 or int(choice) < 0:
                    continue
                self.clear()
                author,title,content = msgs["messages"][int(choice)]
                self.userprint(f"[{author}]: {title}\n===========\n")
                self.userprint(content+"\n")
                self.sock.recv(2048) 


            except ValueError:
                if choice == "exit":
                    break
                else:
                    continue

        self.main_menu()
    def post_msg(self):
        self.clear()
        title = self.userinput("Title Of Message: ").decode("utf-8")
        title = title[0:len(title)-2]


        self.userprint("OK. Write until you press enter with no message.\n")
        cont = ""
        while True:
            val = self.userinput("")
            if val == b'\r\n':
                break

            cont += val[0:len(val)-2].decode("utf-8")
            cont += "\n"
            
        self.userprint("\nPress enter to post!\n")
        self.sock.recv(2048)
        #TODO: Move to another func for retry
        try:
            #{"joe":["lol","lal"]}
            with open("messages.json") as f:
                old = f.read()
                old = json.loads(old)
                f.close()
            old["messages"].append([self.uname,title,cont])
            with open("messages.json","w") as f:
                f.write(json.dumps(old))
                f.close()

            
            print(f"Written a new message to messages.json! Cause: {self.uname}")
            self.main_menu()

        except Exception as e:
            print("ERROR at post_msg(self):",e)




    def main_menu(self):
        self.clear()
        self.sock.send(f"Welcome back, {self.uname}!".encode("utf-8"))
        msg = """\nSelect an option!
[1] User Info
[2] Read Messages 
[3] Post A Message
[4] Logout       
"""
        out = self.userinput(msg).decode("utf-8")
        
        out = out[0:len(out)-2]
        if out == "1":
            self.clear()
            isadmin = (f"{Fore.RED}No{Fore.RESET}",f"{Fore.GREEN}Yes{Fore.RESET}")[self.uname in CONFIG["admins"]]
            self.sock.send(f"User Name: {self.uname}\nPassword: {self.passw}\nAdmin Capabilities: {isadmin}\n".encode("utf-8"))
            self.sock.recv(2048)
            self.main_menu()
        elif out == "4":
            self.sock.close()

        elif out == "3":
            self.post_msg()

        elif out == "2":
            self.read_messages()
            
        else:
            self.main_menu()


    def login(self):
        with open("users.json") as fl:
            users = json.loads(fl.read())
            fl.close()


        self.sock.send("Username:".encode("utf-8"))
        data = self.sock.recv(1024)
        uname = data[0:len(data)-2].decode("utf-8")
        self.sock.send("Password:".encode("utf-8"))
        data = self.sock.recv(1024)
        passw = data[0:len(data)-2].decode("utf-8")

        if uname in users:
            
            if users[uname] == passw:
                print(f"User successfully logged in! Thread {self.tid} is now {uname}!")
                self.authenticated = True
                self.uname = uname
                self.passw = passw
                self.clear()
                self.sock.send(f"Welcome back, {uname}!\n".encode("utf-8"))


    def handler(self):
        #print("Client has been handed off to a User() class.")
        self.clear()
        
        self.sock.send("Welcome to the TestBBS!\n[1]Login\n[2]Create an account.\n".encode("utf-8"))
        self.action = "auth"
        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            if self.action == "auth":
                if data == b'1\r\n':
                    print(self.default + " is trying to log in.")
                    self.login()
                    if self.authenticated == True:
                        self.main_menu()
                    break

                elif data == b'2\r\n':
                    print(self.default + " is trying to sign up. Opening file.")
                    self.authenticated = True
                    self.uname = "admin"

        print("Client closed.")
        self.sock.close()


    def __init__(self,socket: socket.socket,tid) -> None:
        self.sock = socket
        self.action = None
        self.tid = tid
        self.authenticated = False
        self.passw = None
        self.default = socket.getsockname()[0]
        self.uname = None
        self.handler()
