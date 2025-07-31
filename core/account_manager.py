
import json

class AccountManager:
    def __init__(self):
        with open("config/channels.json") as f:
            self.accounts = json.load(f)

    def get_all_accounts(self):
        return self.accounts.items()
