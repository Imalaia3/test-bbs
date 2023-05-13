import json

MESSAGES = "messages.json"
EMAILS   = "pms.json"
USERS    = "users.json"
MSGPLUS  = "msgplus.json"



#TODO/FIXME: Rewrite dbs

def read_messages() -> dict:
    with open(MESSAGES) as m:
        v  = json.loads(m.read())
        m.close()
        return v
    
def post_message(author:str, title:str, content:str) -> None:
    with open(MESSAGES) as oldf:
        old = json.loads(oldf.read())
        oldf.close()
    
    old["messages"].append([author,title,content])
    with open(MESSAGES, "w") as newf:
        newf.write(json.dumps(old))
        newf.close()

    
def write_email(sender:str,receiver:str,subject:str,content:str) -> None:
    with open(EMAILS) as oldf:
        old = json.loads(oldf.read())
        oldf.close()
    
    old["pms"].append([sender,receiver,subject,content])
    with open(EMAILS, "w") as newf:
        newf.write(json.dumps(old))
        newf.close()



def read_emails(receiver:str) -> list:
    with open(EMAILS) as maildb:
        data = json.loads(maildb.read())
        out = []
        for mail in data["pms"]:
            if mail[1] == receiver:
                out.append(mail)


    return out


def query_user(user:str) -> list:
    with open(USERS) as userdb:
        users = json.loads(userdb.read())
        userdb.close()
    if user not in users:
        return None
    return users[user]

def add_user(uname:str, password:str) -> None:
    with open(USERS) as oldf:
        old = json.loads(oldf.read())
        oldf.close()
    
    old[uname] = [password,0]
    with open(USERS, "w") as newf:
        newf.write(json.dumps(old))
        newf.close()

def manage_user(uname:str,rank,color,passw=None):
    with open(USERS) as oldf:
        old = json.loads(oldf.read())
        oldf.close()
    
    if passw == None:
        passw = old[uname][0]
    else:
        passw = passw

    old[uname] = [passw,rank,color]
    with open(USERS, "w") as newf:
        newf.write(json.dumps(old))
        newf.close()


def change_passwd(uname,passw):
    with open(USERS) as oldf:
        old = json.loads(oldf.read())
        oldf.close()
    
    

    old[uname][0] = passw.decode("utf-8")
    print(old)
    with open(USERS, "w") as newf:
        newf.write(json.dumps(old))
        newf.close()


def levelmanager(uname:str,level):
    with open(USERS) as oldf:
        old = json.loads(oldf.read())
        oldf.close()
    
    old[uname][2] = level
    with open(USERS, "w") as newf:
        newf.write(json.dumps(old))
        newf.close()

def getall_users():
    with open(USERS) as userdb:
        users = json.loads(userdb.read())
        userdb.close()

    return users

def deluser(uname):
    with open(USERS) as oldf:
        old = json.loads(oldf.read())
        oldf.close()
    
    del old[uname]
    with open(USERS, "w") as newf:
        newf.write(json.dumps(old))
        newf.close()



class MessagePlus:
    def getall():
        with open(MSGPLUS) as msgf:
            o = json.loads(msgf.read())
            msgf.close()

        return o["messages"]
    
    def query_message(messageID: int):
        ##Might just reuse getall
        with open(MSGPLUS) as msgf:
            messages = json.loads(msgf.read())["messages"]
            msgf.close()

        cMessage = messages[messageID]
        return cMessage
    
    def add_message(uname:str,title:str,content:str) -> None:
        with open(MSGPLUS) as msgf:
            messages = json.loads(msgf.read())
            msgf.close()

        

        #print("a",messages[messageID])
        messages["messages"].append([uname,title,content,[]])
        
        
        with open(MSGPLUS,"w") as msgf:
            msgf.write(json.dumps(messages))
            msgf.close()
    
    def add_comment(messageID: int, username: str, content: str) -> None:
        print("Writing",messageID)
        with open(MSGPLUS) as msgf:
            messages = json.loads(msgf.read())
            msgf.close()

        

        #print("a",messages[messageID])
        messages["messages"][int(messageID)][3].append([username,content])
        
        
        with open(MSGPLUS,"w") as msgf:
            msgf.write(json.dumps(messages))
            msgf.close()



