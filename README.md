<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img style="height:120px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics-space-logo.png?alt=media&token=87727d92-bfb1-43df-bb9e-e2308dfa9b08">
  <div style="margin-top:0.5rem;">
    <h3>Cannabis data and analytics</h3>
  </div>

<https://cannlytics.com>

</div>

🔥Cannlytics is a set of tools to wrangle, curate, augment, analyze, archive, and market cannabis data. The mission of Cannlytics is to help people access cannabis data and analytics. From seed to sale to smoke, Cannlytics can help you organize, analyze, and benefit from your cannabis data. The `cannlytics` package is extensive and you are welcome to use any and all of the components that you find useful.

- [🚀 Installation](#installation)
- [📡 Data](#data)
  <!-- TODO: Write documentation for:
    - cache
    - ccrs
    - gis
    - opendata
    - sales
    - strains
    - web
  -->
  - [📜 COAs](#coas)
- [🔥 Firebase](#firebase)
- [🛡️ Metrc](#metrc)
<!-- TODO: Write documentation for:
  - utils
  - constants
  - compounds
-->

## 🚀 Installation <a name="installation"></a>

You can install the Cannlytics engine from [PyPI](https://pypi.org/project/cannlytics/).

```shell
pip install cannlytics
```

You can also simply clone the repository to get your hands on the Cannlytics source code.

```shell
git clone https://github.com/cannlytics/cannlytics.git
```

You can get the nightly development build by cloning the `app-dev` branch of the repository. The `app-dev` branch is not stable for production, but has the latest and greatest tools that we're working tirelessly to deliver to you shortly.

```shell
git clone -b app-dev https://github.com/cannlytics/cannlytics.git
```

## 🗝️ Authentication <a name="auth"></a>

Cannlytics leverages [🔥Firebase](https://console.firebase.google.com/) for data storage, file storage, and authentication. Use of Firebase is entirely optional and you are welcome to use your favorite database and backend services. If you choose to use Firebase, then you will need to provide credentials for your application. This is typically done by setting a `GOOGLE_APPLICATION_CREDENTIALS` environment variable that points to your service account credentials. For more information on adding authentication to your app, see [the `cannlytics.firebase` documentation](./firebase/readme.md).

## 📡 Data <a name="data"></a>

The `cannlytics.data` module is a toolbox for accessing, collecting, cleaning, augmenting, standardizing, saving, and analyzing cannabis data. See [the `cannlytics.data` documentation](./data/readme.md) for nifty tools to get, standardize, and archive your cannabis data.

### 📜 COAs <a name="coas"></a>

Certificates of analysis (COAs) are abundant for cultivators, processors, retailers, and consumers too, but the data is often locked away. Rich, valuable laboratory data so close, yet so far away! `CoADoc` puts these vital data points in your hands by parsing PDFs and URLs, finding **all the data**, standardizing the data, and cleanly returning the data to you. You can read more about using CoADoc in [the `cannlytics.data.coas` documentation](./data/coas/readme.md).

## 🔥 Firebase <a name="firebase"></a>

The `cannlytics.firebase` module is a wrapper of the [`firebase_admin`](https://pypi.org/project/firebase-admin/) package to make interacting with Firebase services, such as Firestore databases and Firebase Storage buckets, even easier. For more information, see [the `cannlytics.firebase` documentation](./firebase/readme.md).


## 🔰 Metrc <a name="metrc"></a>

Cannlytics integrates with [Metrc](https://metrc.com). You can use the `cannlytics.metrc` module to securely interface with the Metrc API and perform all operations needed for compliance. Simply plug in your vendor and user API keys, specify your state of operations, and you're off to the races.

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
