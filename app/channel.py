from app.message_types import *


class Channel:
    def __init__(self, id, app):
        self.id = id
        self.app = app
        self.users = dict()
        self.user_seq = dict()
        self.user_p2p_unconnected = dict()

    def enter_user(self, new_user):
        other_users = []
        for curr_user in self.users.values():
            message = {
                'type': RESPONSE_TYPE_OTHER_USER_JOIN_CHANNEL,
                'public_udp_address': {
                    'ip': new_user.public_address[0],
                    'port': new_user.public_address[1]
                },
                'private_udp_address': new_user.private_address,
                'uid': new_user.uid
            }
            curr_user.gevent_queue.put(message)

            other_users.append({
                'uid': curr_user.uid,
                'public_udp_address': {
                    'ip': curr_user.public_address[0],
                    'port': curr_user.public_address[1]
                },
                'private_udp_address': curr_user.private_address
            })

        new_user.gevent_queue.put({
            'type': RESPONSE_TYPE_NEW_USER_JOIN_CHANNEL,
            'users': other_users
        })

        self.users[new_user.uid] = new_user

        self.user_seq[new_user.uid] = 0

        new_user.owner_channel = self

        # TODO : support hole punching and make connection of data channel

        self.print_users()

    def exit_user(self, exit_user):
        if exit_user.uid not in self.users or self.users[exit_user.uid].guid != exit_user.guid:
            return

        del (self.users[exit_user.uid])
        del (self.user_seq[exit_user.uid])

        for user in self.users.values():
            user.gevent_queue.put({
                'type': RESPONSE_TYPE_OTHER_USER_EXIT_CHANNEL,
                'exit_user_uid': exit_user.uid
            })

        exit_user.public_address = None
        exit_user.private_address = None

        exit_user.owner_channel = None

        exit_user.gevent_queue.put({
            'type': RESPONSE_TYPE_EXIT_CHANNEL
        })

        # TODO : remove p2p connection and disconnect data channel

        self.print_users()

    def exit_user_by_id(self, user_uid):
        if user_uid not in self.users:
            raise KeyError

        self.exit_user(self.users[user_uid])

    def p2p_status_sync(self, user, uid_list):
        unconnected_users = []
        for user in self.users.values():
            if user.uid not in uid_list:
                unconnected_users.append(user)

        self.user_p2p_unconnected[user.uid] = unconnected_users

    def broadcast(self, line):
        for user in self.users.values():
            user.gevent_queue.put(line)

    def broadcast_by_relay_server(self, relay_server, sender, msg):
        # skip broadcast data if it's not most recent
        if self.user_seq[sender.uid] > msg.seq:
            return

        self.user_seq[sender.uid] = msg.seq

        broadcast_data = msg.to_bytes(sender.uid)

        if msg.type >= 2:
            if sender.uid not in self.user_p2p_unconnected:
                return
            for unconnected_user in self.user_p2p_unconnected[sender.uid]:
                relay_server.socket.sendto(broadcast_data, unconnected_user.public_address)
        else:
            for user in self.users.values():
                relay_server.socket.sendto(broadcast_data, user.public_address)

    def print_users(self):
        print('-- [{}] users --'.format(self.id))
        for user in self.users.values():
            print('guid:{} uid:{}'.format(user.guid, user.uid))
        print('---')
