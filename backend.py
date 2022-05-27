class User:

    users = dict()

    def create(self, username, pwd):
        import hashlib, datetime

        self.chats = list()
        self.id = hex(round(datetime.datetime.now().timestamp()*16777216))[2:]
        self.pwdHash = hashlib.sha256(pwd.encode('utf-16')).hexdigest()
        self.username = username
        User.users[self.id] = self

class Chat:

    chats = dict()

    def create(self, user1, user2):
        import datetime
        self.users = user1.id, user2.id
        self.id = hex(round(datetime.datetime.now().timestamp()*16777216))[2:]
        self.messages = list()
        Chat.chats[self.id] = self

    def add_message(msgData, sender):
        self.messages.append(Message(msgData, sender))

class Message:

    def __init__(self,  msgData, sender):
        import time
        self.time = round(time.time()/60)*60 # round to the nearest minute
        self.data = msgData
        self.sender = sender

def dump():
    import pickle
    users = list(User.users.values())
    with open('data.dat', 'wb') as f:
        pickle.dump(users, f)

def load():
    import pickle
    with open('data.dat', 'rb') as f:
        users = pickle.load(f)
    for i in users:
        User.users[i.id] = i
        for j in i.chats:
            Chat.chats[j.id] = j
