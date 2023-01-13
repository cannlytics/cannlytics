"""
Test Data Market
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 10/11/2021
Updated: 12/21/2021
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports.
import os
import sys

# External imports.
from dotenv import dotenv_values
from ocean_lib.example_config import ExampleConfig
from ocean_lib.ocean.mint_fake_ocean import mint_fake_OCEAN
from ocean_lib.ocean.ocean import Ocean


# Internal imports.
sys.path.append('../../')
from cannlytics.data.market import market # pylint: disable=import-error,wrong-import-position
from cannlytics.firebase import ( # pylint: disable=import-error,wrong-import-position
    initialize_firebase,
    update_document,
)

# First, transfer test ETH to Alice and Bob!
SELLER_KEY = 'TEST_PRIVATE_KEY1'
BUYER_KEY = 'TEST_PRIVATE_KEY2'


def initialize_ocean_market():
    """Initialize a test Ocean data market."""
    local_config = dotenv_values('../../.env')
    os.environ['OCEAN_NETWORK_URL'] = local_config['OCEAN_NETWORK_URL']
    config = ExampleConfig.get_config()
    ocean = Ocean(config)
    return ocean, local_config


def test_publish_data(dataset):
    """Publish a dataset on the data market."""

    # Initialize Ocean market.
    ocean, config = initialize_ocean_market()

    # Mint a test OCEAN.
    os.environ['FACTORY_DEPLOYER_PRIVATE_KEY'] = config['FACTORY_DEPLOYER_PRIVATE_KEY']
    mint_fake_OCEAN(ocean.config)

    # Publish a dataset.
    data_token, asset = market.publish_data(
        ocean,
        config.get(SELLER_KEY),
        files=dataset['files'],
        name=dataset['datatoken_name'],
        symbol=dataset['datatoken_symbol'],
        author=dataset['author'],
        data_license=dataset['license'],
    )

    # Upload the datatoken and asset information.
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['GOOGLE_APPLICATION_CREDENTIALS']
    initialize_firebase()
    ref = f'public/market/datasets/{asset.asset_id}'
    entry = {**dataset, **asset.as_dictionary()}
    update_document(ref, entry)

    return data_token, asset


def test_sell_data(data_token):
    """Sell a dataset on the data market."""

    # Initialize Ocean market.
    ocean, config = initialize_ocean_market()

    # Sell a dataset.
    market.sell_data(
        ocean,
        config.get(SELLER_KEY),
        data_token,
        100,
        fixed_price=True,
    )


def test_buy_data(data_token, asset):
    """Buy a dataset on the data market."""

    # Initialize Ocean market.
    ocean, config = initialize_ocean_market()

    # Buy a dataset.
    seller_wallet = market.get_wallet(
        ocean,
        config.get(SELLER_KEY)
    )
    market.buy_data(
        ocean,
        config.get(BUYER_KEY),
        data_token.address,
        seller_wallet,
        min_amount=2,
        max_amount=5,
    )

    # Download a dataset.
    market.download_data(
        ocean,
        config.get(BUYER_KEY),
        asset.did
    )


# === Test ===
if __name__ == '__main__':

    test_dataset = {
        'sample_file': '',
        'terms': '',
        'price_usd': 3867,
        'datatoken_symbol': 'TD-1',
        'published_at': '2021-10-25',
        'description': 'This is the first test data!',
        'access_type': 'download',
        'file': '',
        'image_url': '',
        'did': '123',
        'author': 'KLS',
        'published_by': 'KLS',
        'datatoken_name': 'test-data',
        'timeout': 0,
        'price_eth': 1,
        'tags': ['test'],
        'title': 'Test Dataset',
        'license': 'CC0: Public Domain',
        'files': [
            {
                "index": 0,
                "contentType": "text/text",
                "url": "https://raw.githubusercontent.com/trentmc/branin/main/branin.arff"
            }
        ]
    }

    # Test publishing a dataset.
    test_data_token, test_asset = test_publish_data(test_dataset)

    # Test selling a dataset.
    test_sell_data(test_data_token)

    # Test buying a dataset.
    test_buy_data(test_data_token, test_asset)
