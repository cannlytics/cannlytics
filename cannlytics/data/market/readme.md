# 🔥Cannlytics 🪙 Cannabis Data Market and 🎑 Algorithm Farm

<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img height="125px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_data_market.png?alt=media&token=f632504b-d00f-4b81-9182-6d5c64956436">
  <img height="125px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_algorithm_farm.png?alt=media&token=5a708351-a5e3-4437-b6bb-19bd6ec339f6">
</div>

Welcome to the [Cannabis Data Market](https://cannabisdatamarket.com) and [Algorithm Farm](https://algorithmfarm.com), firsts of their kind. The idea is that algorithms and data can be published, purchased, and consumed in a decentralized manner as NFTs, through [smart contracts](https://en.wikipedia.org/wiki/Smart_contract), empowering both algorithm and data suppliers and consumers. It's a win-win mechanism that potentially millions can make a good living from creating, curating, and consuming data and algorithms in the cannabis space. Please feel free to begin to share any initial ideas, questions, comments, etc. and join in on the fun as we populate the first cannabis-specific data NFT and algorithm NFT marketplace.

## Introduction to Digital Assets: Data and Algorithm NFTs

Creating distributed ledgers to store information that are transparent, auditable, timestamped, and immutable has become feasible to implement. This allows for the digitization of a vast body of assets, including contracts. This allows records to be reliable and programmable, able to be easily shared to provide value, and capable of being shared in a way to provide value. There are countless opportunities for entrepreneurs and innovators to build new products and services to improve efficiency.
The key features are:

- Universality;
- Increased connectivity;
- Scale and speed never seen before;
- Accessibility of data;
- Price transparency;
- Execution certainty;
- Safety and security;
- No manipulation;
- Trading protocols;
- Prohibitions against market abuse;
- Cyber-resilient;
- Operates efficiently at all times;
- Discloses risks and fees;
- Discloses how your assets are being protected;
- People can opt-in.

That is the beauty of smart contracts, they are built in an open-source manner, transparent and open to all, thanks to tireless work of people voluntarily coming together from around the world. An instance of the service can be re-created anywhere, giving you the freedom to find an option suited to you.

## 🪙 Cannabis Data Market Roadmap

Where the project currently stands:

- [Tests](https://github.com/cannlytics/cannlytics/blob/main/cannlytics/data/market.py) indicate that creating data NFTs, or datatokens, on the Ethereum blockchain is possible, however, the market has only been tested on the [Rinkeby Test Network](https://www.rinkeby.io/#stats).

- Publishing and purchasing datatokens has been tested for [OceanProtocol v3](https://blog.oceanprotocol.com/ocean-protocol-v3-architecture-overview-9f2fab60f9a7), but needs to be updated to [OceanProtocol v4](https://blog.oceanprotocol.com/ocean-v4-overview-1ccd4a7ce150). This is probably going to be a rapidly changing tool, but we can be one of the first companies to utilize it!

- [Algorithm NFT](https://docs.oceanprotocol.com/tutorials/compute-to-data-algorithms/) creation and consumption still needs to be thoroughly tested.

Once the code is tested and we're confident that it works, then we can finish the API endpoints, connect the API endpoints to either the [Cannlytics Website](https://github.com/cannlytics/cannlytics/tree/main/website) or your host of choice, and go live and start earning money! If you want to dip your toes into the Ocean, then here are the examples that we're going to wrap into Cannlytics:

- [Data NFT creation](https://github.com/oceanprotocol/ocean.py/blob/v4main/READMEs/data-nfts-and-datatokens-flow.md);

- [Data NFT market publishing and purchasing](https://github.com/oceanprotocol/ocean.py/blob/v4main/READMEs/marketplace-flow.md);

- [Algorithm NFT creation and consumption](https://github.com/oceanprotocol/ocean.py/blob/v4main/READMEs/c2d-flow.md).

At the end of the day, creating data and algorithm NFT marketplaces will be a game-changer for the cannabis industry, so, please join in on the fun!

## 🎑 The Algorithm Farm - An Algorithm NFT Marketplace

The idea is for data collection, processing, and analysis algorithms and data to be <a href="https://github.com/cannlytics/cannlytics-ai">open source</a> and available for purchase as NFTs on a market.

A rough list of tasks that need to be done, include:

1. Refactor:
  - [ ] Write thorough doc-strings for all functions.
  - [ ] Allow selling data as a pool.
  - [ ] Allow user to pass a Wallet instead of private_key.

2. Publish assets metadata and associated services:
  - [ ] Each asset is assigned a unique DID and a DID Document (DDO).
  - [ ] The DDO contains the asset's services including the metadata.
  - [ ] The DID is registered on-chain with a URL of the metadata store to retrieve the DDO from

  ```python
  asset = ocean.assets.create(metadata, publisher_wallet)
  ```

3. Publish data NFT and algorithm NFT functions wrapped in `market.py`.
