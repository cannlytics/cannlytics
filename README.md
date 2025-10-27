# 🔥Cannlytics

[Cannlytics](https://cannlytics.com) is a set of tools to wrangle, augment, archive, and analyze cannabis data. From seed to sale to the effects, Cannlytics can help you access, organize, analyze, and generally benefit from available cannabis data. You are welcome to use any and all of the tools that you find useful.

## Installation <a name="installation"></a>

You can install the `cannlytics` Python package from [PyPI](https://pypi.org/project/cannlytics/).

```shell
pip install cannlytics
```

You can clone the repository to get your hands on the Cannlytics source code.

```shell
git clone https://github.com/cannlytics/cannlytics.git
```

## Data <a name="data"></a>

The `cannlytics.data` module is a toolbox for accessing, collecting, cleaning, augmenting, standardizing, saving, and analyzing cannabis data. See [the `cannlytics.data` documentation](./data/readme.md) for nifty tools to get, standardize, and archive your cannabis data.

### COAs <a name="coas"></a>

Certificates of analysis (COAs) are abundant for cultivators, processors, retailers, and consumers too, but the data is often locked away. Rich, valuable laboratory data so close, yet so far away! `CoADoc` puts these vital data points in your hands by parsing PDFs and URLs, finding **all the data**, standardizing the data, and cleanly returning the data to you. You can read more about using CoADoc in [the `cannlytics.data.coas` documentation](./data/coas/readme.md).

## Metrc <a name="metrc"></a>

You can use the `cannlytics.metrc` module to securely interface with the Metrc API and perform all operations needed for compliance. Simply plug in your vendor and user API keys, specify your state of operations, and you're off to the races.

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

See [the `cannlytics.metrc` documentation](./cannlytics/metrc/readme.md) for more information and examples on how you can interface with the Metrc API.


## License

```
Copyright (c) 2020-2025 Cannlytics

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
