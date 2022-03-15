"""
Data Market | Cannlytics
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 10/11/2021
Updated: 10/11/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

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

"""
# Internal packages.
from datetime import datetime
import os
import yaml

# External packages.
try:
    from ocean_lib.common.agreements.service_types import ServiceTypes
    from ocean_lib.services.service import Service
    from ocean_lib.data_provider.data_service_provider import DataServiceProvider
    from ocean_lib.models.btoken import BToken # BToken is ERC20
    from ocean_lib.ocean.ocean import Ocean
    from ocean_lib.web3_internal.constants import ZERO_ADDRESS
    from ocean_lib.web3_internal.currency import pretty_ether_and_wei, to_wei, from_wei
    from ocean_lib.web3_internal.wallet import Wallet
except:
    # FIXME: ocean_lib doesn't like the App Engine environment.
    pass


def get_wallet(ocean, private_key):
    """Get a user's wallet given their private key.
    Args:
        ocean ():
        private_key (str):
    Returns:

    """
    return Wallet(ocean.web3, private_key, ocean.config.block_confirmations)

def initialize_market(env_file='env.yaml'):
    """Initialize an Ocean data marketplace.
    Args:
        env_file (str): An environment variable file,
            `env.yaml` by default.
    Returns:
    
    """
    config = None
    with open(env_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    os.environ['ocean_network_url'] = config['OCEAN_NETWORK_URL']
    return Ocean(config)


def publish_data(
        ocean,
        private_key,
        files,
        name,
        symbol,
        author,
        data_license='CC0: Public Domain',
):
    """Publish a dataset on the Ocean marketplace.
    Publish metadata and service attributes on-chain.
    The service urls will be encrypted before going on-chain.
    They're only decrypted for datatoken owners upon consume.
    Args:
        ocean ():
        private_key (str):
        files (list):
        name (str):
        symbol (str):
        author (str):
        data_license (str): The license for the data,
            `CC0: Public Domain` by default.
    Returns:
        ()
    """
    wallet = Wallet(ocean.web3, private_key, ocean.config.block_confirmations)
    assert wallet.web3.eth.get_balance(wallet.address) > 0, 'need ETH'
    print('Proceeding with wallet:', wallet.address)
    data_token = ocean.create_data_token(name, symbol, wallet, blob=ocean.config.metadata_cache_uri)
    # return data_token
    token_address = data_token.address
    print('Created token:', token_address)
    date_created = datetime.now().isoformat()
    metadata =  {
        'main': {
            'type': 'dataset',
            'name': name,
            'author': author,
            'license': data_license,
            'dateCreated': date_created,
            'files': files,
        }
    }
    service_attributes = {
        'main': {
            'name': 'dataAssetAccessServiceAgreement',
            'creator': wallet.address,
            'timeout': 3600 * 24,
            'datePublished': date_created,
            'cost': 1.0, # <don't change, this is obsolete>
        }
    }
    service_endpoint = DataServiceProvider.get_url(ocean.config)
    # FIXME:
    download_service = Service(
        service_endpoint=service_endpoint,
        service_type=ServiceTypes.ASSET_ACCESS,
        attributes=service_attributes,
    )
    assert wallet.web3.eth.get_balance(wallet.address) > 0, 'need ETH'
    asset = ocean.assets.create(
        metadata,
        wallet,
        # services=[download_service],
        # service_descriptors=[],
        data_token_address=token_address
    )
    print('Created asset:', asset.data_token_address)
    assert token_address == asset.data_token_address
    return data_token, asset


def sell_data(
        ocean,
        private_key,
        data_token,
        amount,
        fixed_price=True,
):
    """Sell a dataset on the Ocean market.
    Mint the datatokens.
    In the create() step below, ganache OCEAN is needed.
    Finally, Approve the datatoken for sale.
    Args:
        ocean ():
        wallet ():
        data_token ():
        amount ():
        fixed_price (bool): Whether or not to sell the data at a fixed price.
    Returns:
        (bool): Returns True if successful.
    """
    wallet = Wallet(ocean.web3, private_key, ocean.config.block_confirmations)
    data_token.mint(wallet.address, to_wei(amount), wallet)
    OCEAN_token = BToken(ocean.web3, ocean.OCEAN_address)
    assert OCEAN_token.balanceOf(wallet.address) > 0, 'need OCEAN'
    data_token.approve(
        ocean.exchange._exchange_address,
        to_wei(amount),
        wallet
    )
    return True


def buy_data(
        ocean,
        private_key,
        token_address,
        seller_wallet,
        min_amount,
        max_amount,
):
    """Buy a dataset on the market.
    Define wallet, verify that there is enough ganache ETH and OCEAN.
    Create an exchange_id for a new exchange.
    Args:
        ocean ():
        private_key (str):
        token_address (str):
        seller_wallet (Wallet):
        min_amount (float):
        max_amount (float):
    Returns:

    """
    wallet = Wallet(ocean.web3, private_key, ocean.config.block_confirmations)
    assert ocean.web3.eth.get_balance(wallet.address) > 0, 'need ganache ETH'
    OCEAN_token = BToken(ocean.web3, ocean.OCEAN_address)
    assert OCEAN_token.balanceOf(wallet.address) > 0, 'need ganache OCEAN'
    exchange_id = ocean.exchange.create(token_address, to_wei(min_amount), seller_wallet)
    tx_result = ocean.exchange.buy_at_fixed_rate(
        to_wei(min_amount),
        wallet,
        to_wei(max_amount),
        exchange_id,
        token_address,
        seller_wallet.address
    )
    assert tx_result, 'failed buying data tokens at fixed rate.'
    # FIXME:
    # print(f"Bob has {pretty_ether_and_wei(data_token.balanceOf(bob_wallet.address), data_token.symbol())}.")
    # assert data_token.balanceOf(wallet.address) >= to_wei(1), "Bob didn't get 1.0 datatokens"



def download_data(ocean, private_key, did):
    """Download a dataset that is in a user's possession.
    Points to the service object, send datatoken to the service,
    and then downloads the dataset files. If the connection breaks,
    then the request can be made again with the order_tx_id.
    Args:
        ocean ():
        private_key ():
        did (str): Dataset ID.
    Returns:

    """
    wallet = Wallet(ocean.web3, private_key, ocean.config.block_confirmations)
    fee_receiver = ZERO_ADDRESS # could also be market address
    asset = ocean.assets.resolve(did)
    service = asset.get_service(ServiceTypes.ASSET_ACCESS)
    quote = ocean.assets.order(asset.did, wallet.address, service_index=service.index)
    order_tx_id = ocean.assets.pay_for_service(
        ocean.web3,
        quote.amount,
        quote.data_token_address,
        asset.did,
        service.index,
        fee_receiver,
        wallet,
        service.get_c2d_address()
    )
    try:
        file_path = ocean.assets.download(
            asset.did,
            service.index,
            wallet,
            order_tx_id,
            destination='./'
        )
        return file_path
    except:
        return order_tx_id
