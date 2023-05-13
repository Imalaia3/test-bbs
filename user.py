import socket
import json
from colorama import Fore,Cursor
import random
import time
import dbmanager as db
with open("config.json") as f:
    CONFIG = json.loads(f.read())
    f.close()


RANK_COLORS = {
    -1 : Fore.RED,
    0  : Fore.WHITE,
    1  : Fore.CYAN,
    2  : Fore.CYAN,
    3  : Fore.CYAN,
    4  : Fore.LIGHTGREEN_EX,
    5  : Fore.LIGHTGREEN_EX,
    6  : Fore.LIGHTGREEN_EX,
    7  : Fore.LIGHTGREEN_EX,
    8  : Fore.LIGHTGREEN_EX,
    9  : Fore.YELLOW
}

ULTRADEBUG = False
def debugprint(msg):
    if ULTRADEBUG:
        print("[DEBUG]",msg)

BUFFER_SIZE = 1024  #### Max buffer size in bytes as per the TELNET spec.



MBOX  = f"""
    
{Fore.RED}      _________
    .`.        `.
   /   \ .======.\\
   |   | |______||
   |   |   _____ |
   |   |  /    / |
   |   | /____/  |
   | _ |         |
   |/ \|.-"```"-.|
{Fore.WHITE}   `` |||      |||
{Fore.RESET}      `"`      `"
"""



class User:
    #might move to utils.py

    def userinput(self,msg:str,strip=False):
        self.sock.send(msg.encode("utf-8"))
        data = self.sock.recv(BUFFER_SIZE)
        debugprint("Requested input")
        if not data:
           return None
        
        if not strip:
            return data
        return data[:-2]
    
    def userprint(self,msg,end="\n"):
        debugprint("Requested print")
        msg = msg+end
        self.sock.send(str(msg).encode("utf-8"))
 
    ##let's implement a quick renderer
    def onelinebox(self,entries:list):
        el = 0
        for e in entries:
            el += len(e)
        
        top = "+"
        for e in entries:
            top += "-"*len(e)
            top += "+"

        middle = "|"
        for e in entries:
            middle += e + "|"
        

        output = f"{top}\n{middle}\n{top}"
        self.userprint(output)


    def radiobox(self,entries:list):
        #FIXME: Suppport 0 indexing
        o = ""
        for c,e in enumerate(entries):
            o += f"[{c+1}] {e}\n"

        self.userprint(o)
        while True:
            sel = self.userinput(f"Selection (1-{str(len(entries))}) ").decode("utf-8")
            sel = sel[0:len(sel)-2]
            if not sel.isnumeric():
                continue
            if int(sel) > len(entries) or int(sel) < 1 :
                continue

            break
        return int(sel)




    def limitinput(self,msg:str,maxi=10):
        while True:
            self.userprint(msg,end="")
            self.userprint(("_"*maxi)+"|",end="")
            self.userprint(Cursor.BACK(maxi),end="")
            v = self.userinput("").decode("utf-8")
            v = v[0:len(v)-2]
            if len(v) > maxi:
                self.userprint("\r")
                continue
            else:
                return v
            
    def multiline_input(self):
        out = ""
        while True:
            tmp = self.userinput("",strip=False)
            if tmp == b'\r\n':
                break
            out += tmp[:-2].decode("utf-8") + "\n"

        return out[:-1]
    
    def adv_multiline_input(self):
        lines = []
        while True:
            tmp = self.userinput("",strip=False)
            if tmp == b'\r\n':
                break
            if tmp == b'\x1b[A\r\n':
                tmp = self.userinput("(Editing Line Above) ",strip=False)
                lines[-1] = tmp[:-2].decode("utf-8") + "\n"
            else:
                lines.append(tmp[:-2].decode("utf-8") + "\n")

        
        res = ""
        for line in lines:
            res += line
        
        return line[:-1]
    
    def scroll_text(self,msg,waitms=30):
        for c in msg:
            self.userprint(c,end="")
            time.sleep(waitms/1000)
            
    



    def clear(self):
        self.sock.send("\033[2J\033[H".encode("utf-8"))
        self.userprint(CONFIG["splash"],end="")
        self.userprint(f"The time is: {time.ctime()}.\n")
        debugprint("cleared screen")


    def read_messages(self):
        self.clear()
        self.userprint(MBOX)
        self.userprint("All Messages:")
        msgs = db.read_messages()
        debugprint("Queried messages.")

        output = ""
        for c,message in enumerate(msgs["messages"]):
            author  = message[0]
            title   = message[1]
            #content = message[2]
            output += f"({c})[{author}] {title}\n"


        self.userprint(output,end="")
        while True:
            choice = self.userinput("\nSelect a message (exit to exit): ")[:-2].decode("utf-8")
            try:
                if int(choice) > len(msgs["messages"])-1 or int(choice) < 0:
                    continue
                self.clear()
                author,title,content = msgs["messages"][int(choice)]
                self.userprint(f"[{author}]: {title}\n===========")
                self.userprint(content)
                self.sock.recv(BUFFER_SIZE) 


            except ValueError:
                if choice == "exit":
                    break
                else:
                    continue

        self.main_menu()
    def post_msg(self):
        self.clear()
        title = self.userinput("Title Of Message: ")[:-2].decode("utf-8")

        self.userprint("OK. Write until you press enter with no message.")
        #cont = self.multiline_input()
        cont  = self.adv_multiline_input()

        self.userprint("\nPress enter to post!")
        self.sock.recv(BUFFER_SIZE)
        #TODO: Move to another func for retry
        try:
            #{"joe":["lol","lal"]}
            db.post_message(self.uname,title,cont)

            
            print(f"[FILE] Written a new message to messages.json! Cause: {self.uname}")
            self.main_menu()

        except Exception as e:
            print("[ERROR] post_msg(self):",e)

    
    def read_mailbox(self):
        self.clear()
        """self.userprint(MBOX + "\n")
        self.userinput("")
        self.main_menu()"""

        my_messages = db.read_emails(self.uname)
        out = ""
        for c,message in enumerate(my_messages):
            out+= f"({c+1}) [From: {message[1]}] {message[2]}\n"

        self.userprint(out)
        while True:
            choice = self.userinput("\nSelect a message (exit to exit): ")
            choice = choice[0:len(choice)-2].decode("utf-8")
            try:
                if int(choice) > len(my_messages)-1 or int(choice) < 0:
                    continue
                self.clear()
                author  = my_messages[int(choice)][0]
                title   = my_messages[int(choice)][2]
                content = my_messages[int(choice)][3]
                self.userprint(f"[{author}]: {title}\n===========")
                self.userprint(content)
                self.sock.recv(BUFFER_SIZE) 


            except ValueError:
                if choice == "exit":
                    break
                else:
                    continue

        self.main_menu()

    def send_mail(self):
        self.clear()
        title = self.userinput("Title Of Message: ")[:-2].decode("utf-8")

        
        to = self.userinput("Name of receiver: ")[:-2].decode("utf-8")


        self.userprint("\nOK. Write until you press enter with no message.")
        cont = self.multiline_input()
            
        self.userprint("\nPress enter to post!")
        self.sock.recv(BUFFER_SIZE)
        #TODO: Move to another func for retry
        try:
            #{"joe":["lol","lal"]}
            db.write_email(self.uname,to,title,cont)

            
            print(f"[FILE] Written a new message to pms.json! Cause: {self.uname}->{to}")
            self.main_menu()

        except Exception as e:
            print("[ERROR] send_mail(self):",e)



    def play_games(self):
        msg = """
Play some Games!\nSelect one from below:
[1] Number Guesser
[2] Adding Game

        """
        while True:


            self.clear()
            self.userprint(msg)
            choice = self.userinput("Select one")[:-2].decode("utf-8")

            if choice == "1":
                self.clear()
                self.userprint("Pick a number from 1-50!")
                pc_choice = random.randrange(1,50)
                print(pc_choice)
                while True:
                    choice = self.userinput(">")[:-2].decode("utf-8")
                    if choice == "exit":
                        self.main_menu()


                    try:
                        choice = int(choice)
                    except KeyError:
                        continue

                    if choice > pc_choice:
                        self.userprint(f"{Fore.LIGHTRED_EX}Lower!{Fore.RESET}")
                        continue
                    elif choice < pc_choice:
                        self.userprint(f"{Fore.LIGHTRED_EX}Higher!{Fore.RESET}")
                        continue
                    elif choice == pc_choice:
                        self.userprint(f"{Fore.GREEN}YOU FOUND THE NUMBER!\nIt was {str(pc_choice)}!\n{Fore.RESET}")
                        oldlev = db.query_user(self.uname)[2]
                        db.levelmanager(self.uname,oldlev+1)
                        self.userprint(f"{Fore.YELLOW}1 level point has been added to your account!{Fore.RESET}")
                        self.userinput("Press ENTER to return to the main menu...\n")
                        self.main_menu()

            if choice == "2":
                self.clear()
                self.userprint("Number Adder!\nSpeed mode! Sovle 10 questions in the least time possible!\n")
                self.userinput("Press enter to begin!")
                solves = []
                for i in range(10):
                    left  = random.randrange(0,50)
                    right = random.randrange(0,50)
                    res = left + right
                    print(res)
                    

                    while True:
                        try:
                            before = time.time_ns() / 1000000
                            out = int(self.userinput(f"{left}+{right}=",strip=True))
                            after = time.time_ns() / 1000000
                        except ValueError:
                            continue
                        
                        if out == res:
                            print("Found")
                            solves.append(after-before)
                        
                        break
                
                timeAvg = sum(solves) / len(solves)
                self.userprint(f"You solved {len(solves)}/10 equations! With an average of {int(timeAvg)}ms per solve!")
                award = 0
                for solve in solves:
                    if solve > 5000:
                        continue
                    award += 1

                self.userprint(f"{Fore.YELLOW}{award} points have been added to your account!{Fore.RESET}")
                self.userinput("Press Enter to main menu")
                oldlev = db.query_user(self.uname)[2]
                db.levelmanager(self.uname,oldlev+award)
                self.main_menu()





    def use_adv_messages(self):
        self.clear()
        self.userprint("TestBBS Advanced Messaging System!")
        

        #choice = self.userinput("Select a message (exit to exit): ")
        while True:
            messages = db.MessagePlus.getall()
            for c,message in enumerate(messages):
                self.userprint(f"({c})[{message[0]}] {message[1]}")

            
            choice = self.userinput("\nSelect a message (exit to exit or, new to post a new message): ")[:-2].decode("utf-8")
            try:
                if int(choice) > len(messages)-1 or int(choice) < 0:
                    continue
                

                while True:
                    self.clear()
                    messages = db.MessagePlus.getall()
                    message = messages[int(choice)]
                    self.userprint(f"[{message[0]}] {message[1]}\n===================")
                    self.userprint(message[2] + "\n===================\n\n")

                    for comment in message[3]:
                        cmnt = ""
                        for word in comment[1].split(" "):
                            if "@" in word and self.uname == word.strip("@"):
                                cmnt += Fore.YELLOW + word + Fore.RESET + " "
                                continue
                            cmnt += word + " "


                        

                        cdata = f"{comment[0]}: {cmnt}\n" + "-"*(8)
                        self.userprint(cdata)


                    nchoice = self.userinput("\nSelect an option ([1]Exit [2]Reply): ")[:-2].decode("utf-8")
                    if nchoice == "1":
                        break
                    elif nchoice == "2":
                        


                        self.userprint("OK. Write until you press enter with no message.")
                        cont = self.adv_multiline_input()
                            
                        self.userprint("\nPress enter to post!")
                        self.sock.recv(BUFFER_SIZE)

                        
                        print("[FILE] Trying to post comment",cont)
                        db.MessagePlus.add_comment(choice,self.uname,cont)
                        break

                        



            except ValueError:
                if choice == "exit":
                    break
                if choice == "new":
                    self.clear()
                    title = self.userinput("Select A Title For The Post: ",strip=True).decode("utf-8")
                    self.clear()
                    self.userprint(f"Posting: {title}\n")
                    cont  = self.adv_multiline_input()
                    
                    self.userinput("Press ENTER to post")
                    db.MessagePlus.add_message(self.uname,title,cont)
                    self.clear()
                    
                else:
                    continue     
        self.main_menu()


    def admin_tools(self):
        if not self.isadmin:
            self.exitreason = "IllegalOperationError"
            self.sock.close()
            return

        while True:
            self.clear()
            self.userprint(f"TestBBS Control Panel. Currently logged in as: {self.uname}")
            op = str(self.radiobox([
                "User Management",
                "Post Management",
                "AMS Management",
                f"{Fore.RED}Shutdown Server{Fore.RESET}",
                "Exit",
            ]))

            if op == "5":
                break
            elif op == "4":
                o = self.userinput("Kill Server (y/N)",True).decode("utf-8")
                if o.upper() == "Y":
                    self.exitreason = "ServerKillCommand"
                    break
                else:
                    self.main_menu()    

                
            elif op == "1":
                #User Management system
                usrs = db.getall_users()
                opt = self.radiobox(list(usrs.keys()))
                user = usrs[list(usrs.keys())[opt-1]]
                seluname = list(usrs.keys())[opt-1]
                while True:
                    self.clear()
                    self.userprint(f"Managing User: {seluname}")
                    opt = self.radiobox(["Exit", "Delete User", "Change Password"])
                    if opt == 2:
                        db.deluser(seluname)
                        self.userprint("User successfully deleted!")
                        print(f"[USER/FILE] User {seluname} deleted. Cause: {self.uname}")
                    elif opt == 1:
                        break

                    elif opt == 3:
                        passw = self.userinput("New Password: ",strip=True)
                        if passw == self.userinput("\nConfirm Password: ",strip=True):
                            
                            db.change_passwd(seluname, passw)
                            self.userprint(f"The password for {seluname} is now {passw}!")
                            self.userinput("")
        if self.exitreason != "ServerKillCommand":
            self.main_menu()

    def main_menu(self):
        self.clear()
        self.sock.send(f"Welcome back, {self.uname}!\n".encode("utf-8"))

        

        if self.isadmin:
            print("amadming")
            out = str(self.radiobox([
            "User Info",
            "Read Messages", 
            "Post A Message",
            "BBS Info",
            "Read Mailbox",
            "Send Mail",
            "Logout",
            "Games",
            "Advanced Messages / Threads",
            "Admin Tools"
        ]))
        else:
            out = str(self.radiobox([
            "User Info",
            "Read Messages", 
            "Post A Message",
            "BBS Info",
            "Read Mailbox",
            "Send Mail",
            "Logout",
            "Games",
            "Advanced Messages / Threads"
        ]))



        if out == "1":
            self.clear()
            isadmin = (f"{Fore.RED}No{Fore.RESET}",f"{Fore.GREEN}Yes{Fore.RESET}")[self.uname in CONFIG["admins"]]
            uQuery = db.query_user(self.uname)
            rank  = uQuery[1]
            level = uQuery[2]
            self.sock.send(f"User Name: {self.uname}\nPassword: {self.passw}\nAdmin Capabilities: {isadmin}\nCurrent Rank: {RANK_COLORS[rank]} {str(rank)}{Fore.YELLOW} (Level: {str(level)}){Fore.RESET}".encode("utf-8"))
            self.sock.recv(BUFFER_SIZE)
            self.main_menu()

        elif out == "2":
            self.read_messages()

        elif out == "3":
            self.post_msg()

        elif out == "4":
            self.userprint(f"Goodbye, {self.uname}!\nHave a great rest of your day!\n")
            self.sock.close()
            self.exitreason = "MainMenu"


        elif out == "5":
            self.clear()
            with open("users.json") as u:
                usrs = u.read()
                usrs = json.loads(usrs)
                u.close()
                usrs = usrs.keys()
            member_count = len(usrs)
            admins = CONFIG["admins"]
            adm = '\n'.join(admins)
            self.userprint(f"{CONFIG['description']}\n\nThis BBS has {member_count} members and {len(admins)} admins!!.\n\nAdmins: \n{adm}\n")
            self.sock.recv(BUFFER_SIZE)
            pass
        
        

        elif out == "6":
            self.read_mailbox()

        

        elif out == "7":
            self.send_mail()

        elif out == "8":
            self.play_games()

        elif out == "9":
            self.use_adv_messages()

        elif out == "10" and self.isadmin:
            self.admin_tools()

        else:
            self.main_menu()


    def login(self):
        with open("users.json") as fl:
            users = json.loads(fl.read())
            fl.close()



        uname = self.userinput("Username: ", True).decode("utf-8")
        passw = self.userinput("Password: ", True).decode("utf-8")
        #print(f"{uname}:{passw}")

        if uname in users:
            
            if users[uname][0] == passw:
                print(f"[USER] User successfully logged in! Thread {self.tid} is now {uname}!")
                self.authenticated = True
                self.uname = uname
                self.passw = passw
                self.isadmin = self.uname in CONFIG["admins"]
                self.clear()
                self.sock.send(f"Welcome back, {uname}!\n".encode("utf-8"))


    def signup(self):
        uname = self.userinput("Username: ", True).decode("utf-8")
        passw = self.userinput("Password: ", True).decode("utf-8")

        if db.query_user(uname):
            print(f"[USER] Sign-up attempt failed. Cause: UserExistsError ({uname})")
            self.userprint("User already exists!")
            self.sock.close()
            return
        db.add_user(uname,passw)
        self.uname = uname
        self.authenticated = True
        self.passw = passw
        self.isadmin = self.uname in CONFIG["admins"]
        print(f"[USER] User successfully signed in! Thread {self.tid} is now {uname}!")
        
        self.clear()
        self.sock.send(f"Welcome back, {uname}!\n".encode("utf-8"))

    def handler(self):
        #print("Client has been handed off to a User() class.")
        self.clear()
        self.userprint("Welcome to the TestBBS!\n")
        
        while True:
            data = str(self.radiobox(["Login","Create an account"]))
            if data == "1":
                print("[USER] "+self.default + " is trying to log in.")
                self.login()
                if self.authenticated == True:
                    self.main_menu()
                    print(self.uname in CONFIG["admins"])
                    
                break

            elif data == "2":
                print("[USER] " +self.default + " is trying to sign up. Opening file.")
                self.signup()
                if self.authenticated == True:
                    self.isadmin = self.uname in CONFIG["admins"]
                    self.main_menu()
                break

        print("[USER] Client closed.")
        self.sock.close()


    def __init__(self,socket: socket.socket,tid:int) -> None:
        self.sock = socket
        self.tid = tid
        self.authenticated = False
        self.passw = None
        self.uname = None
        self.default = socket.getsockname()[0]
        self.exitreason = "Unspecified"
        self.isadmin = False
        self.handler()


if __name__ == "__main__":
    #Temp setver.py bypass
    from os import system
    system("python3 server.py 2023")