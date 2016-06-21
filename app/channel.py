from app.message_types import *


class Channel:
    def __init__(self, id, app):
        self.id = id
        self.app = app
        self.users = dict()

    def enter_user(self, new_user):
        other_users = []
        for user in self.users.values():
            message = {
                'type': RESPONSE_TYPE_OTHER_USER_JOIN_CHANNEL,
                'public_udp_address': new_user.public_address[0],
                'private_udp_address': new_user.private_address[0]
            }
            user.gevent_queue.put(message)

            other_users.append({
                'uid': user.uid,
                'public_udp_address': user.public_address[0],
                'private_udp_address': user.private_address[0]
            })

        new_user.gevent_queue.put({
            'type': RESPONSE_TYPE_NEW_USER_JOIN_CHANNEL,
            'users': other_users
        })

        self.users[new_user.uid] = new_user
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
