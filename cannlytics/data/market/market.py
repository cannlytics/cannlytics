"""
Data Market | Cannlytics
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 10/11/2021
Updated: 6/26/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

TODO:

    1. Refactor
        - Write docstrings.
        - Allow selling data as a pool.
        - Allow user to pass a Wallet instead of private_key.

    2. Publish assets metadata and associated services
        - Each asset is assigned a unique DID and a DID Document (DDO)
        - The DDO contains the asset's services including the metadata
        - The DID is registered on-chain with a URL of the metadata store
            to retrieve the DDO from
        `asset = ocean.assets.create(metadata, publisher_wallet)`

Read up:

    - https://www.quicknode.com/guides/web3-sdks/estimating-gas-price-using-pending-transactions-in-python

"""
# Internal packages.
from datetime import datetime
import os
import yaml

# External packages.
from dotenv import dotenv_values
try:
    from ocean_lib.ocean.ocean import Ocean
    from ocean_lib.web3_internal.wallet import Wallet
    from ocean_lib.web3_internal.currency import from_wei
except:
    pass

# External packages.
# try:
#     from ocean_lib.common.agreements.service_types import ServiceTypes
#     from ocean_lib.services.service import Service
#     from ocean_lib.data_provider.data_service_provider import DataServiceProvider
#     from ocean_lib.models.btoken import BToken # BToken is ERC20
#     from ocean_lib.ocean.ocean import Ocean
#     from ocean_lib.web3_internal.constants import ZERO_ADDRESS
#     from ocean_lib.web3_internal.currency import pretty_ether_and_wei, to_wei, from_wei
#     from ocean_lib.web3_internal.wallet import Wallet
# except:
#     # FIXME: ocean_lib doesn't like the App Engine environment.
#     pass


# def create_datatoken(wallet, nft, symbol, value):
#     """Create a datatoken related to a given NFT.
#     """
#     datatoken = nft.create_datatoken(value, symbol, from_wallet=wallet)
#     print(f"Created datatoken. Its address is {datatoken.address}")
#     return datatoken


# def publish_data_nft(ocean, wallet, symbol, value):
#     """Create Ocean instance, wallet, and publish an NFT token.
#     """
#     data_nft = ocean.create_data_nft(
#         value,
#         symbol,
#         wallet,
#         # token_uri='https://cannlytics.com/nft/',
#     )
#     print(f"Created data NFT. Its address is {data_nft.address}")
#     return data_nft



#-----------------------------------------------------------------------
# Test
#-----------------------------------------------------------------------

# Get the user's private key.
env_vars = dotenv_values('../../.env')
user_private_key = env_vars['TEST_PRIVATE_KEY1']
os.environ['ocean_network_url'] = env_vars['OCEAN_NETWORK_URL']
os.environ['ocean_network_url'] = env_vars['ADDRESS_FILE']
# =~/.ocean/ocean-contracts/artifacts/address.json

# Define data NFT value and symbol.


# Initialize the data ocean.
from ocean_lib.example_config import ExampleConfig
config = ExampleConfig.get_config()
ocean = Ocean(config)
# ocean = Ocean({
#     'address_file': '~/.ocean/ocean-contracts/artifacts/address.json',
#     'network_url': 'http://127.0.0.1:8545',
#     # 'network': 'https://rinkeby.infura.io/v3/1f0c7b5c219448f5a767a6ff0820d3e8',
#     # 'metadataCacheUri': 'https://aquarius.rinkeby.oceanprotocol.com',
#     # 'providerUri': 'https://provider.rinkeby.oceanprotocol.com',
# })

# Examine config.
print(f"config.network_url = '{ocean.config.network_url}'")
print(f"config.block_confirmations = {ocean.config.block_confirmations.value}")
print(f"config.metadata_cache_uri = '{ocean.config.metadata_cache_uri}'")
print(f"config.provider_url = '{ocean.config.provider_url}'")

# Get the user's wallet.
user_wallet = Wallet(
    ocean.web3,
    user_private_key,
    ocean.config.block_confirmations,
    ocean.config.transaction_timeout,
)
print(f"user_wallet.address = '{user_wallet.address}'")

# Check that the user has ETH.
assert user_wallet.web3.eth.get_balance(user_wallet.address) > 0, 'need ETH'

# Get OCEAN token balance.
print(f"Address of OCEAN token: {ocean.OCEAN_address}")
OCEAN_token = ocean.OCEAN_token
OCEAN_balance_in_wei = OCEAN_token.balanceOf(user_wallet.address)
OCEAN_balance_in_ether = from_wei(OCEAN_balance_in_wei)
print(f"Balance: {OCEAN_balance_in_ether} OCEAN")
if OCEAN_balance_in_wei == 0:
  print("WARNING: you don't have any OCEAN yet")

# TODO: Estimate gas price to display to user.

# Create a data NFT.
symbol = 'CAN-NFT-1'
value = '[{"test": "yes"}]'
data_nft = ocean.create_data_nft(
    value,
    symbol,
    user_wallet,
    owner=user_wallet.address,
    # token_uri='https://cannlytics.com/nft/',
)
print(f"Data NFT token name: {data_nft.token_name()}")
print(f"Data NFT token symbol: {data_nft.symbol()}")

# Create a datatoken for the data NFT.
symbol = 'CAN-DT-1'
value = 'Datatoken 1'
datatoken = data_nft.create_datatoken(value, symbol, user_wallet)
print(f"Datatoken name: {datatoken.token_name()}")
print(f"Datatoken symbol: {datatoken.symbol()}")

# Optional: Do both at the same time?
# ocean.create_nft_with_erc20()

# TODO: Save IDs / data to Firestore!!!
gas_price = from_wei(data_nft.get_gas_price(data_nft.web3))


# TODO: Get IDs from Firestore.
# - Initiate token?


#-----------------------------------------------------------------------
# Algorithm publishing and consumption.
#-----------------------------------------------------------------------

# Get a preview of what you will pay for an algorithm compute job.
# ocean.ocean_compute.get_c2d_environments(service.service_endpoint)
# ocean.retrieve_provider_fees_for_compute(datasets, algorithm_data, consumer_address, compute_environment, duration)


#-----------------------------------------------------------------------
# OLD v3
#-----------------------------------------------------------------------

# def get_wallet(ocean, private_key):
#     """Get a user's wallet given their private key.
#     Args:
#         ocean ():
#         private_key (str):
#     Returns:

#     """
#     return Wallet(ocean.web3, private_key, ocean.config.block_confirmations)


# def initialize_market(env_file='env.yaml'):
#     """Initialize an Ocean data marketplace.
#     Args:
#         env_file (str): An environment variable file,
#             `env.yaml` by default.
#     Returns:
    
#     """
#     config = None
#     with open(env_file, 'r') as f:
#         config = yaml.load(f, Loader=yaml.FullLoader)
#     os.environ['ocean_network_url'] = config['OCEAN_NETWORK_URL']
#     return Ocean(config)


# def publish_data(
#         ocean,
#         private_key,
#         files,
#         name,
#         symbol,
#         author,
#         data_license='CC0: Public Domain',
# ):
#     """Publish a dataset on the Ocean marketplace.
#     Publish metadata and service attributes on-chain.
#     The service urls will be encrypted before going on-chain.
#     They're only decrypted for datatoken owners upon consume.
#     Args:
#         ocean ():
#         private_key (str):
#         files (list):
#         name (str):
#         symbol (str):
#         author (str):
#         data_license (str): The license for the data,
#             `CC0: Public Domain` by default.
#     Returns:
#         ()
#     """
#     wallet = Wallet(ocean.web3, private_key, ocean.config.block_confirmations)
#     assert wallet.web3.eth.get_balance(wallet.address) > 0, 'need ETH'
#     print('Proceeding with wallet:', wallet.address)
#     data_token = ocean.create_data_token(name, symbol, wallet, blob=ocean.config.metadata_cache_uri)
#     # return data_token
#     token_address = data_token.address
#     print('Created token:', token_address)
#     date_created = datetime.now().isoformat()
#     metadata =  {
#         'main': {
#             'type': 'dataset',
#             'name': name,
#             'author': author,
#             'license': data_license,
#             'dateCreated': date_created,
#             'files': files,
#         }
#     }
#     service_attributes = {
#         'main': {
#             'name': 'dataAssetAccessServiceAgreement',
#             'creator': wallet.address,
#             'timeout': 3600 * 24,
#             'datePublished': date_created,
#             'cost': 1.0, # <don't change, this is obsolete>
#         }
#     }
#     service_endpoint = DataServiceProvider.get_url(ocean.config)
#     # FIXME:
#     download_service = Service(
#         service_endpoint=service_endpoint,
#         service_type=ServiceTypes.ASSET_ACCESS,
#         attributes=service_attributes,
#     )
#     assert wallet.web3.eth.get_balance(wallet.address) > 0, 'need ETH'
#     asset = ocean.assets.create(
#         metadata,
#         wallet,
#         # services=[download_service],
#         # service_descriptors=[],
#         data_token_address=token_address
#     )
#     print('Created asset:', asset.data_token_address)
#     assert token_address == asset.data_token_address
#     return data_token, asset


# def sell_data(
#         ocean,
#         private_key,
#         data_token,
#         amount,
#         fixed_price=True,
# ):
#     """Sell a dataset on the Ocean market.
#     Mint the datatokens.
#     In the create() step below, ganache OCEAN is needed.
#     Finally, Approve the datatoken for sale.
#     Args:
#         ocean ():
#         wallet ():
#         data_token ():
#         amount ():
#         fixed_price (bool): Whether or not to sell the data at a fixed price.
#     Returns:
#         (bool): Returns True if successful.
#     """
#     wallet = Wallet(ocean.web3, private_key, ocean.config.block_confirmations)
#     data_token.mint(wallet.address, to_wei(amount), wallet)
#     OCEAN_token = BToken(ocean.web3, ocean.OCEAN_address)
#     assert OCEAN_token.balanceOf(wallet.address) > 0, 'need OCEAN'
#     data_token.approve(
#         ocean.exchange._exchange_address,
#         to_wei(amount),
#         wallet
#     )
#     return True


# def buy_data(
#         ocean,
#         private_key,
#         token_address,
#         seller_wallet,
#         min_amount,
#         max_amount,
# ):
#     """Buy a dataset on the market.
#     Define wallet, verify that there is enough ganache ETH and OCEAN.
#     Create an exchange_id for a new exchange.
#     Args:
#         ocean ():
#         private_key (str):
#         token_address (str):
#         seller_wallet (Wallet):
#         min_amount (float):
#         max_amount (float):
#     Returns:

#     """
#     wallet = Wallet(ocean.web3, private_key, ocean.config.block_confirmations)
#     assert ocean.web3.eth.get_balance(wallet.address) > 0, 'need ganache ETH'
#     OCEAN_token = BToken(ocean.web3, ocean.OCEAN_address)
#     assert OCEAN_token.balanceOf(wallet.address) > 0, 'need ganache OCEAN'
#     exchange_id = ocean.exchange.create(token_address, to_wei(min_amount), seller_wallet)
#     tx_result = ocean.exchange.buy_at_fixed_rate(
#         to_wei(min_amount),
#         wallet,
#         to_wei(max_amount),
#         exchange_id,
#         token_address,
#         seller_wallet.address
#     )
#     assert tx_result, 'failed buying data tokens at fixed rate.'
#     # FIXME:
#     # print(f"Bob has {pretty_ether_and_wei(data_token.balanceOf(bob_wallet.address), data_token.symbol())}.")
#     # assert data_token.balanceOf(wallet.address) >= to_wei(1), "Bob didn't get 1.0 datatokens"



# def download_data(ocean, private_key, did):
#     """Download a dataset that is in a user's possession.
#     Points to the service object, send datatoken to the service,
#     and then downloads the dataset files. If the connection breaks,
#     then the request can be made again with the order_tx_id.
#     Args:
#         ocean ():
#         private_key ():
#         did (str): Dataset ID.
#     Returns:

#     """
#     wallet = Wallet(ocean.web3, private_key, ocean.config.block_confirmations)
#     fee_receiver = ZERO_ADDRESS # could also be market address
#     asset = ocean.assets.resolve(did)
#     service = asset.get_service(ServiceTypes.ASSET_ACCESS)
#     quote = ocean.assets.order(asset.did, wallet.address, service_index=service.index)
#     order_tx_id = ocean.assets.pay_for_service(
#         ocean.web3,
#         quote.amount,
#         quote.data_token_address,
#         asset.did,
#         service.index,
#         fee_receiver,
#         wallet,
#         service.get_c2d_address()
#     )
#     try:
#         file_path = ocean.assets.download(
#             asset.did,
#             service.index,
#             wallet,
#             order_tx_id,
#             destination='./'
#         )
#         return file_path
#     except:
#         return order_tx_id
