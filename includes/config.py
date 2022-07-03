from includes.setup._envs import Envs
from includes.setup._logging import start_logger
import includes.setup._paths

envs = Envs()
log = start_logger()

creds = dict(
    key=envs.spot_key,
    secret=envs.spot_secret,
    passphrase=envs.api_passphrase,
    is_sandbox=False,
    url="https://api.kucoin.com",
)

# key=envs.futures_key
# secret=envs.futures_secret
