# `BudSpender` | Cannabis Receipt Parser

<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img width="150px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fbud_spender.png?alt=media&token=e0de707b-9c18-44b9-9944-b36fcffd9fd3">
</div>

Your cannabis receipts hold a lot of data, put that data to work for you with `BudSpender`. This AI-powered tool parses cannabis receipts into well-structured data that can be used for trending, analytics, and however you please.

## Installation

Simply make sure that you have `cannlytics` installed:

```sh
pip install cannlytics
```

## Usage

Initialize a `BudSpender` parsing client:

```py
from cannlytics.data import BudSpender

# Initialize a COA parser.
parser = BudSpender()
```

Parse a single receipt:

```py
# Parse a receipt.
filename = 'receipt-2023-04-20.jpeg'
data = parser.parse(filename)
```

Parse a folder of receipts:

```py
# Parse a folder of receipts.
folder = './receipts'
data = parser.parse(filename)
```
