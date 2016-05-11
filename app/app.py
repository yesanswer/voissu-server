class App:
    def __init__(self, id):
        self.id = id
        self.channels = dict()
        self.users = dict()

    def enter_user(self, user):
        self.users[user.uid] = user
        print('[system][{}] new connected user uid : {}'.format(self.id, user.uid))

    def exit_user(self, user):
        user.disconnect()
        if user.uid in self.users:
            if self.users[user.uid].guid == user.guid:
                del(self.users[user.uid])

    def exit_user_by_id(self, user_uid):
        if user_uid not in self.users:
            raise KeyError

        self.exit_user(self.users[user_uid])

    def enter_channel(self):
        pass

    def exit_channel(self):
        pass

    def get_user(self, uid):
        return self.users[uid] if uid in self.users else None

    def broadcast(self, line):
        for user in self.users.values():
            user.gevent_queue.put(line)
