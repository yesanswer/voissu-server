from app.message_types import *


class Channel:
    def __init__(self, id, app):
        self.id = id
        self.app = app
        self.users = dict()
        self.user_list = None
        self.user_seq = dict()

    def enter_user(self, new_user):
        other_users = []
        for user in self.users.values():
            message = {
                'type': RESPONSE_TYPE_OTHER_USER_JOIN_CHANNEL,
                'public_udp_address': {
                    'ip': new_user.public_address[0],
                    'port': new_user.public_address[1]
                },
                'private_udp_address': new_user.private_address
            }
            user.gevent_queue.put(message)

            other_users.append({
                'uid': user.uid,
                'public_udp_address': {
                    'ip': user.public_address[0],
                    'port': user.public_address[1]
                },
                'private_udp_address': user.private_address
            })

        new_user.gevent_queue.put({
            'type': RESPONSE_TYPE_NEW_USER_JOIN_CHANNEL,
            'users': other_users
        })

        self.users[new_user.uid] = new_user
        self.user_list = self.users.values()

        self.user_seq[new_user.uid] = 0

        new_user.channel = self
        # TODO : support hole punching and make connection of data channel

    def exit_user(self, exit_user):
        if exit_user.uid in self.users:
            if self.users[exit_user.uid].guid == exit_user.guid:
                del (self.users[exit_user.uid])
                del (self.user_seq[exit_user.uid])

        for user in self.users.values():
            user.gevent_queue.put({
                'type': RESPONSE_TYPE_EXIT_CHANNEL
            })

        self.user_list = self.users.values()

        exit_user.public_address = None
        exit_user.private_address = None

        exit_user.channel = None

        # TODO : remove p2p connection and disconnect data channel

    def exit_user_by_id(self, user_uid):
        if user_uid not in self.users:
            raise KeyError

        self.exit_user(self.users[user_uid])

    def broadcast(self, line):
        for user in self.user_list:
            user.gevent_queue.put(line)

    def broadcast_by_relay_server(self, relay_server, sender, msg):
        # skip broadcast data if it's not most recent
        if self.user_seq[sender.uid] > msg.seq:
            return

        self.user_seq[sender.uid] = msg.seq

        broadcast_data = msg.to_bytes(sender.uid)

        for user in self.user_list:
            relay_server.socket.sendto(broadcast_data, user.public_address)
