from typing import Optional

from aptos_sdk import ed25519
from aptos_sdk.account_address import AccountAddress
from aptos_sdk.client import RestClient
from aptos_sdk.account import Account


class AptosClient(RestClient):
    node_url = 'https://fullnode.mainnet.aptoslabs.com/v1'

    def __init__(self, private_key: str, proxy: Optional[str] = None):
        super().__init__(AptosClient.node_url)
        self.private_key = private_key
        self.signer = Account.load_key(self.private_key)
        self.address = AccountAddress.from_key(ed25519.PrivateKey.from_hex(private_key).public_key()).hex()
        self.proxy = proxy

        # self.client_config.max_gas_amount = 100000
        # print(f'__init__ create Client. max_gas_amount: {self.client_config.max_gas_amount}')
