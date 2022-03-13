"""
Title | Project

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 
Updated: 
License: MIT License <https://github.com/cannlytics/cannlytics-ai/blob/main/LICENSE>
"""


# Initialize a Socrata client.
# app_token = os.environ.get('APP_TOKEN', None)
# client = Socrata('opendata.mass-cannabis-control.com', app_token)

# # Get sales by product type.
# products = client.get('xwf2-j7g9', limit=2000)
# products_data = pd.DataFrame.from_records(products)

# # Get licensees.
# licensees = client.get("hmwt-yiqy", limit=2000)
# licensees_data = pd.DataFrame.from_records(licensees)

# # Get the monthly average price per ounce.
# avg_price = client.get("rqtv-uenj", limit=2000)
# avg_price_data = pd.DataFrame.from_records(avg_price)

# # Get production stats (total employees, total plants, etc.)
# production = client.get("j3q7-3usu", limit=2000, order='saledate DESC')
# production_data = pd.DataFrame.from_records(production)