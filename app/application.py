from app.channel import Channel


class Application:
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

    def enter_channel(self, channel_id, user):
        if channel_id not in self.channels:
            new_channel = Channel(channel_id, self)
            self.channels[new_channel.id] = new_channel

        self.channels[channel_id].enter_user(user)

    def exit_channel(self, channel_id, user):
        if channel_id not in self.channels:
            # error
            pass

        channel = self.channels[channel_id]
        channel.exit_user(user)

        if len(channel.users) == 0:
            del (self.channels[channel.id])

    def get_user(self, uid):
        return self.users[uid] if uid in self.users else None

    def check_exist_channel(self, channel_id):
        return channel_id in self.channels

    def broadcast(self, line):
        for user in self.users.values():
            user.gevent_queue.put(line)
