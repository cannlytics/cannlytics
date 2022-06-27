# Cannlytics Data Module

A core component of Cannlytics is facilitating the access to cannabis data. The module, `cannlytics.data`, is intended to be a vast well that anyone can use to access rich cannabis data.

## CannPatent

*Under development*

Find and curate data for cannabis patents. In particular, `cannpatent.py` collects detailed data for plant patents. Subsequent intellectual property (IP) analytics provide actionable insights for cannabis cultivar inventors and consumers. For example, cultivators can use the methodology to predict if a particular cultivar would make a good patent candidate given its lab results. Consumers can find the nearest patented strain to a set of lab results printed on a cultivar's label.

## Market

*Under development*

The idea is for data collection, processing, and analysis algorithms and data to be <a href="https://github.com/cannlytics/cannlytics-ai">open source</a> and available for purchase as NFTs on a market.

Roadmap:

1. Refactor
  - Write thorough docstrings for all functions.
  - Allow selling data as a pool.
  - Allow user to pass a Wallet instead of private_key.

2. Publish assets metadata and associated services
  - Each asset is assigned a unique DID and a DID Document (DDO)
  - The DDO contains the asset's services including the metadata
  - The DID is registered on-chain with a URL of the metadata store
      to retrieve the DDO from
  `asset = ocean.assets.create(metadata, publisher_wallet)`

3. Publish data NFT and algorithm NFT functions wrapped in `market.py`.

## OpenData

*Under development*

An instance of this class communicates with the Cannabis Control Commission of the Commonwealth of Massachusetts' Open Data catalog.

- [Massachusetts Cannabis Control Commission Data Catalog](https://masscannabiscontrol.com/open-data/data-catalog/)

Roadmap:

- TODO: Create a data guide.
- FIXME: SQL queries do not appear to work.
