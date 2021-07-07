# Worksheets

Cannlytics provides Excel workbooks [powered with Python](https://www.xlwings.org/) macros to provide you with a mechanism to collect data in a way that may be familiar or preferable to your analysts. Worksheets are based on the [Department of Ecology of the State of Washington Bench sheets and control charts for labs](https://ecology.wa.gov/Regulations-Permits/Permits-certifications/Laboratory-Accreditation/Bench-sheets-and-control-charts-for-labs).

Users can customize the *Worksheet* tab, with data being referenced on the *Upload* where it will be read using [`xlwings`](https://docs.xlwings.org/en/stable/quickstart.html) and uploaded to Firestore.

Organizations are assigned the standard data models on creation and are given a set of worksheets to facilitate importing data. The worksheets can be customized to a lab's preferences.
