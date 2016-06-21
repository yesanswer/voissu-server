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
                'public_udp_address': new_user.public_address,
                'private_udp_address': new_user.private_address
            }
            user.gevent_queue.put(message)

            other_users.append({
                'uid': user.uid,
                'public_udp_address': user.public_address,
                'private_udp_address': user.private_address
            })

        new_user.gevent_queue.put({
            'type': RESPONSE_TYPE_NEW_USER_JOIN_CHANNEL,
            'users': other_users
        })

        self.users[new_user.uid] = new_user
        # TODO : support hole punching and make connection of data channel

    def exit_user(self, exit_user):
        if exit_user.uid in self.users:
            if self.users[exit_user.uid].guid == exit_user.guid:
                del (self.users[exit_user.uid])

        for user in self.users.values():
            user.gevent_queue.put({
                'type': RESPONSE_TYPE_EXIT_CHANNEL
            })

        exit_user.public_address = None
        exit_user.private_address = None

        # TODO : remove p2p connection and disconnect data channel

    def exit_user_by_id(self, user_uid):
        if user_uid not in self.users:
            raise KeyError

        self.exit_user(self.users[user_uid])

    def broadcast(self, line):
        for user in self.users.values():
            user.gevent_queue.put(line)
