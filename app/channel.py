class Channel:
    def __init__(self, id, app):
        self.id = id
        self.app = app
        self.users = dict()
