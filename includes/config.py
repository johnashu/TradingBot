from includes.setup._envs import Envs
from includes.setup._logging import start_logger
from includes.setup._paths import *
from tools.file_op import open_json
import sys

sys.dont_write_bytecode = True

verbose = True

envs = Envs()
log = start_logger(verbose=verbose)

creds = dict(
    key=envs.spot_key,
    secret=envs.spot_secret,
    passphrase=envs.api_passphrase,
    is_sandbox=False,
    url="https://api.kucoin.com",
)

metadata = open_json(pairs_metadata_path)

# key=envs.futures_key
# secret=envs.futures_secret
