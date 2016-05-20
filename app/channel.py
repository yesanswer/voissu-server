class Channel:
    def __init__(self, id, app):
        self.id = id
        self.app = app
        self.users = dict()

    def enter_user(self, user):
        self.users[user.guid] = user
        # TODO : support hole punching and make connection of data channel

    def exit_user(self, user):
        if user.uid in self.users:
            if self.users[user.uid].guid == user.guid:
                del (self.users[user.uid])
        # TODO : remove p2p connection and disconnect data channel
        pass

    def exit_user_by_id(self, user_uid):
        if user_uid not in self.users:
            raise KeyError

        self.exit_user(self.users[user_uid])

    def broadcast(self, line):
        for user in self.users.values():
            user.gevent_queue.put(line)
