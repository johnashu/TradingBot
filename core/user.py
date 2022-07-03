# User
from kucoin.client import User


class Account:
    def __init__(self, creds) -> None:
        self.client = User(**creds)

    async def get_quota(self, token: str) -> str:
        quota = self.client.get_withdrawal_quota(token)
        return quota

    async def get_account_data(self, currency: str, account_type: str = "trade") -> str:
        account = self.client.get_account_list(
            currency=currency, account_type=account_type
        )
        return account
