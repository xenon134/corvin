class User:

    users = set()

    def create(username, pwd):
        if User.for_username(username): # it not None
            return False
        import hashlib
        user = User()
        user.chats = list()
        user.pwdHash = hashlib.sha256(pwd.encode('utf-16')).digest()
        user.username = username
        user.authtoken = None
        User.users.add(user)
        print('User added: ' + user.username)
        return True

    def for_username(username):
        for i in User.users:
            if i.username == username:
                return i

    def login(self):
        import os
        self.authtoken = os.urandom(32)
        return self.authtoken.hex()

    def for_authtoken(at):
        at = bytes.fromhex(at)
        for i in User.users:
            if i.authtoken == at:
                return i

    def check_password(self, pwd):
        import hashlib
        return hashlib.sha256(pwd.encode('utf-16')).digest() == self.pwdHash

    def changePassword(self, pwd):
        import hashlib
        self.pwdHash = hashlib.sha256(pwd.encode('utf-16')).digest()

    def allChats(self):
        import json
        return json.dumps([{
            'with': i.withUser(self).username,
            'messages': [{
                'sent': j[0] == self,
                'data': j[1]
            } for j in i.messages]
        } for i in self.chats])

    def sendMsg(self, to, msgData):
        for i in self.chats:
            if to in i.users:
                chat = i
                break
        else: # chat does not exist
            chat = Chat({self, to})
            to.chats.insert(0, chat)
            self.chats.insert(0, chat)
        chat.messages.insert(0, (self, msgData))

class Chat:

    def __init__(self, users):
        self.users = users
        self.messages = list()

    def withUser(self, oneUser):
        try:
            return [i for i in self.users if i != oneUser][0]
        except IndexError:
            return None

import pickle, threading, time
with open('data.dat', 'rb') as f:
    usrs = pickle.load(f)
for i in usrs:
    User.users.add(i)
print(len(User.users), 'users loaded.')

updatePeriod = 10 # in seconds
def updateFile():
    while True:
        time.sleep(updatePeriod)
        usrs = list(User.users)
        with open('data.dat', 'wb') as f:
            pickle.dump(usrs, f)
th = threading.Thread(target=updateFile)
th.setDaemon(True)
th.start()
