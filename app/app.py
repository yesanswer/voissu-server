class App:
    def __init__(self, id):
        self.id = id
        self.channels = dict()
        self.users = dict()

    def enter_user(self, user):
        self.users[user.uid] = user
        print('[system][{}] new connected user uid : {}'.format(self.id, user.uid))

    def exit_user(self, user):
        del(self.users[user.uid])

    def enter_channel(self):
        pass

    def exit_channel(self):
        pass

    def get_user(self, uid):
        return self.users[uid] if uid in self.users else None

    def broadcast(self, line):
        for user in self.users.values():
            user.gevent_queue.put(line)
