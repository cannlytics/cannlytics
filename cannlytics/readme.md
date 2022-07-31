<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img style="height:180px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics-engine-logo.png?alt=media&token=85e11a96-ac74-479d-a69b-e61a3a47b4d2">
  <div style="margin-top:0.5rem;">
    <h3>Simple, easy, cannabis analytics.</h3>
  </div>

<https://cannlytics.com>

[![License: MIT](https://img.shields.io/badge/License-MIT-darkgreen.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/pypi/v/cannlytics.svg)](https://pypi.org/project/cannlytics)
[![PyPI download month](https://img.shields.io/pypi/dm/cannlytics.svg)](https://pypi.python.org/pypi/cannlytics/)

</div>

🔥 Cannlytics is simple, easy-to-use, **end-to-end** cannabis analytics software designed to make your data and information accessible. We believe that everyone in the cannabis industry should be able to access their rich, valuable data quickly and easily and that everyone will be better off for it. The Cannlytics Engine comes with **batteries included**, but you are always welcome to supercharge your setup with modifications and custom components.

- [🚀 Installation](#installation)
- [👩‍🏫 Documentation](#documentation)
- [🗝️ Authentication, Data, and File Management](#development)
- [🧐 Traceability](#automation)
- [👩‍🔬 Testing](#testing)
- [🤝 Contributing](#contributing)
- [💖 Support](#support)
- [🏛️ License](#license)

## 🚀 Installation <a name="installation"></a>

You can install the Cannlytics engine from [PyPI](https://pypi.org/project/cannlytics/).

```shell
pip install cannlytics
```

You can also simply clone the repository to get your hands on the Cannlytics source code.

```shell
git clone https://github.com/cannlytics/cannlytics-engine.git
```

## 👩‍🏫 Documentation <a name="documentation"></a>

Please refer to the [Cannlytics developer documentation](https://docs.cannlytics.com/developers/development/) for detailed information about the module and various use cases.

## 🗝️ Authentication, Data, and File Management

Cannlytics leverages [Firebase](https://console.firebase.google.com/) by default for a database, file storage, and authentication. You can [refer to the documentation](https://docs.cannlytics.com/cannlytics/firebase/firebase/) for instructions on how to setup your Firebase project for use with Cannlytics.

## 🧐 Traceability <a name="traceability"></a>

Cannlytics supports [Metrc](https://api-ca.metrc.com/Documentation) out-of-the-box. Simply plug in your API keys and you're off to the races.

```py
from cannlytics import metrc

# Initialize a Metrc API client.
track = metrc.authorize(
    'your-vendor-api-key',
    'your-user-api-key',
    primary_license='your-user-license-number',
    state='ma',
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

## 👩‍🔬 Testing <a name="testing"></a>

You can run tests with code coverage with `pytest`.

```
pytest --cov=cannlytics tests/
```

## 🤝 Contributing <a name="contributing"></a>

Contributions are always welcome! You are encouraged to submit issues, functionality, and features that you want to be addressed. You can also develop your own new features, fix known issues, and add documentation, tests, and examples. Anyone is welcome to contribute anything. Please see the [contributing guide](https://docs.cannlytics.com/developers/contributing) for more information.

## 💖 Support <a name="support"></a>

Cannlytics is made available with ❤️ and your good will. Please consider making a contribution to help us continue crafting useful tools and data pipelines for you. Thank you 🙏

| Provider | Link |
|-|-|
| 👐 OpenCollective | <https://opencollective.com/cannlytics-company/donate> |
| 💸 PayPal Donation | <https://paypal.me/cannlytics> |
| 💵 Venmo Donation | <https://www.venmo.com/u/cannlytics> |
| 🪙 Bitcoin donation address| 34CoUcAFprRnLnDTHt6FKMjZyvKvQHb6c6 |
| ⚡ Ethereum donation address | 0xa466d0893e3d4f584c5a7aec1104b9f1d541cf1c |

## 🏛️ License <a name="license"></a>

```
Copyright (c) 2021-2022 Cannlytics and the Cannabis Data Science Team

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
