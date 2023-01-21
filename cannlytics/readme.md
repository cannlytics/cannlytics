<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img style="height:120px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics-space-logo.png?alt=media&token=87727d92-bfb1-43df-bb9e-e2308dfa9b08">
  <div style="margin-top:0.5rem;">
    <h3>Cannabis data science and analytics.</h3>
  </div>

<https://cannlytics.com>

[![License: MIT](https://img.shields.io/badge/License-MIT-orange.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/pypi/v/cannlytics.svg)](https://pypi.org/project/cannlytics)
[![PyPI download month](https://img.shields.io/pypi/dm/cannlytics.svg?color=orange)](https://pypi.python.org/pypi/cannlytics/)

</div>

🔥Cannlytics is a set of useful tools to wrangle, curate, augment, analyze, archive, and market cannabis data. The mission of Cannlytics is to help cannabis data and analytics be accessible. From seed to sale and beyond, Cannlytics can help you organize, analyze, and profit from your cannabis data. The `cannlytics` package is extensive and you are welcome to use any and all of the components that you find useful.

- [🚀 Installation](#installation)
- [🗝️ Authentication](#auth)
- [📡 Data](#data)
  - [CoAs](#coas)
  - [Market](#market)
- [🔥 Firebase](#firebase)
- [⚗️ LIMS](#lims)
- [🛡️ Metrc](#metrc)
- [📈 Statistics](#stats)
- [🏛️ License](#license)

## 🚀 Installation <a name="installation"></a>

You can install the Cannlytics engine from [PyPI](https://pypi.org/project/cannlytics/).

```shell
pip install cannlytics
```

You can also simply clone the repository to get your hands on the Cannlytics source code.

```shell
git clone https://github.com/cannlytics/cannlytics.git
```

You can get the nightly development build by cloning the `dev` branch of the repository. The `dev` branch is not stable for production, but has the latest and greatest tools that we're working tirelessly to deliver to you shortly.

```shell
git clone -b dev https://github.com/cannlytics/cannlytics.git
```

## 🗝️ Authentication <a name="auth"></a>

Cannlytics leverages [🔥Firebase](https://console.firebase.google.com/) by default for data storage, file storage, and authentication. Use of Firebase is entirely optional and you are welcome to use your favorite database and backend services. If you choose to use Firebase, then you will need to provide credentials for your application by setting a `GOOGLE_APPLICATION_CREDENTIALS` environment variable that points to your service account credentials. For more information on adding authentication to your app, see [the `cannlytics.firebase` documentation](https://github.com/cannlytics/cannlytics/tree/main/cannlytics/firebase).

## 📡 Data <a name="data"></a>

The `cannlytics.data` module is a large toolbox for accessing, collecting, cleaning, augmenting, standardizing, saving, and analyzing cannabis data. See [the `cannlytics.data` documentation](https://github.com/cannlytics/cannlytics/tree/main/cannlytics/data) for more information on how to manage your cannabis data.

### COAs <a name="coas"></a>

Certificates of analysis (COAs) are abundant for cultivators, processors, retailers, and consumers too, but the data is often locked away. Rich, valuable laboratory data so close, yet so far away! `CoADoc` puts these vital data points in your hands by parsing PDFs and URLs, finding **all the data**, standardizing the data, and cleanly returning the data to you. You can read more about using CoADoc in [the `cannlytics.data.coas` documentation](https://github.com/cannlytics/cannlytics/tree/main/cannlytics/data/coas).

### Market <a name="market"></a>

Welcome to the [Cannabis Data Market](https://cannabisdatamarket.com) and [Algorithm Farm](https://algorithmfarm.com), firsts of their kind. The idea is that algorithms and data can be published, purchased, and consumed in a decentralized manner as NFTs, through [smart contracts](https://en.wikipedia.org/wiki/Smart_contract), empowering both algorithm and data suppliers and consumers. It's a win-win mechanism that potentially millions can make a good living from creating, curating, and consuming data and algorithms in the cannabis space. Please feel free to begin to share any initial ideas, questions, comments, etc. and join in on the fun as we populate the first cannabis-specific data NFT and algorithm NFT marketplace. You can read more about using the data market in [the `cannlytics.data.market` documentation](https://github.com/cannlytics/cannlytics/tree/main/cannlytics/data/market).

## 🔥 Firebase <a name="firebase"></a>

The `cannlytics.firebase` module is a wrapper of the [`firebase_admin`](https://pypi.org/project/firebase-admin/) package to make interacting with Firebase services, such as Firestore databases and Firebase Storage buckets, even easier. For more information, see [the `cannlytics.firebase` documentation](https://github.com/cannlytics/cannlytics/tree/main/cannlytics/firebase).

## ⚗️ LIMS <a name="lims"></a>

The `cannlytics.lims.instruments` submodule provides tools to collect data generated by scientific instruments typically used by analytical labs that test cannabis. You can see [the `cannlytics.lims` documentation](https://github.com/cannlytics/cannlytics/tree/main/cannlytics/lims) to see how to automatically collect results from your scientific instruments.

## 🛡️ Metrc <a name="metrc"></a>

Cannlytics supports [Metrc](https://metrc.com) out-of-the-box. You can use the `cannlytics.metrc` module to securely interface with the Metrc API and perform all operations needed for compliance. Simply plug in your vendor and user API keys, specify your state of operations, and you're off to the races.

```py
from cannlytics import metrc

# Initialize a Metrc API client.
track = metrc.authorize(
    'your-vendor-api-key',
    'your-user-api-key',
    primary_license='your-user-license-number',
    state='ok',
)
```

Producer / processor workflow:

```py
# Get a plant by it's ID.
plant = track.get_plants(uid='123')

# Change the growth phase from vegetative to flowering.
plant.flower(tag='your-plant-tag')

# Move the flowering plant to a new room.
plant.move(location_name='The Flower Room')

# Manicure useable cannabis from the flowering plant.
plant.manicure(harvest_name='Old-Time Moonshine', weight=4.20)

# Harvest the flowering plant.
plant.harvest(harvest_name='Old-Time Moonshine', weight=420)
```

Lab workflow:

```py
# Post lab results.
track.post_lab_results([{...}, {...}])

# Get a tested package.
test_package = track.get_packages(label='abc')

# Get the tested package's lab result.
lab_results = track.get_lab_results(uid=test_package.id)
```

Retail workflow:

```py
# Get a retail package.
package = track.get_packages(label='abc')

# Create a sales receipts.
track.create_receipts([{...}, {...}])

# Get recent receipts.
sales = track.get_receipts(action='active', start='2021-04-20')

# Update the sales receipt.
sale = track.get_receipts(uid='420')
sale.total_price = 25
sale.update()
```

See [the `cannlytics.metrc` documentation](https://github.com/cannlytics/cannlytics/tree/main/cannlytics/metrc) for more information and examples on how you can interface with the Metrc API.

## 📈 Statistics <a name="stats"></a>

The `cannlytics.stats` submodule contains a number of functions for estimating, saving, and using statistical models. You can read more about the statistical tools in [the `cannlytics.stats` documentation](https://github.com/cannlytics/cannlytics/tree/main/cannlytics/data/coas).

## 🏛️ License <a name="license"></a>

```
Copyright (c) 2021-2023 Cannlytics and The Cannabis Data Science Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Please cite the following if you use the code examples in your research:

```bibtex
@misc{cannlytics2022,
  title={Cannabis Data Science},
  author={Skeate, Keegan and Rice, Charles and O'Sullivan-Sutherland, Candace},
  journal={https://github.com/cannlytics/cannabis-data-science},
  year={2023}
}
```
