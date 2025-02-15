class Password:

    def __init__(self):
        # stores a dictionary of usernames and passwords
        self.users_passwords = {}

    def sign_up(self, username, password):
        if username in self.users_passwords:
            return f"Please enter a new username. {username} already taken."
        else:
            self.users_passwords[username] = password

    def login(self, username, password):
        if username in self.users_passwords:
            if password == self.users_passwords[username]:
                return True
            else:
                return False
            
        else:
            return f"{username} not found. Please create an account or re-enter your username."