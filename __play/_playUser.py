# User
from kucoin.client import User
from includes.config import *


class Account:
    def __init__(self, creds) -> None:
        self.client = User(**creds)

    def get_quota(self, token: str) -> str:
        quota = self.client.get_withdrawal_quota(token)
        return quota

    def get_account_data(self, currency: str, account_type: str) -> str:
        account = self.client.get_account_list(
            currency=currency, account_type=account_type
        )
        return account


if __name__ == "__main__":
    from includes.config import *

    currency = "ONE"
    account_type = "trade"

    t = Account(creds)
    usdt = t.get_account_data(currency, account_type)
    print(usdt)
[
    {
        "id": "608683d093a6df000685f0e6",
        "currency": "ONE",
        "type": "trade",
        "balance": "40",
        "available": "40",
        "holds": "0",
    }
]
