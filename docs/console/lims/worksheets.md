# Worksheets

Cannlytics provides Excel workbooks [powered with Python](https://www.xlwings.org/) macros to provide you with a mechanism to collect data in a way that may be familiar or preferable to your analysts. Worksheets are based on the [Department of Ecology of the State of Washington Bench sheets and control charts for labs](https://ecology.wa.gov/Regulations-Permits/Permits-certifications/Laboratory-Accreditation/Bench-sheets-and-control-charts-for-labs).

<img src="/assets/images/screenshots/screenshot_worksheets_measurements.png"/>

Users can customize the *Worksheet* tab, with data being referenced on the *Upload* where it will be read using [`xlwings`](https://docs.xlwings.org/en/stable/quickstart.html) and uploaded to Firestore. Organizations are assigned the standard data models on creation and are given a set of worksheets to facilitate importing data.

!!! Tip
    The worksheets can be customized to a lab's preferences.

<!-- ## Setup

The worksheets include import and upload buttons that can be used to expediently import and upload data. The buttons leverage Python-powered Excel macros by utilizing `xlwings`. You can setup xlwings on your computer by first installing a Python distribution and the xlwings package. If you are using Anaconda, then xlwings should already be installed. If you need to install xlwings, then simply run

```shell
pip install xlwings
```

You will need to install the xlwings Excel add-in:

```shell
xlwings addin install
```

> If you need to add the `xlwings.bas` module to a new worksheet. See the [xlwings documentation](https://docs.xlwings.org/en/v0.9.3/vba.html?highlight=python#xlwings-vba-module) for detailed instructions for how to install the module.

## Uploading Data


## Importing Data -->
