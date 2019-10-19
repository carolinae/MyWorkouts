import uuid


class User:
    def __init__(self, username, password, email, user_id=None):
        self.username = username
        self.password = password
        self.email = email

        if user_id is None:
            self.user_id = str(uuid.uuid4())
        else:
            self.user_id = user_id
