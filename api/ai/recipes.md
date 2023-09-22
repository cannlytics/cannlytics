# BudderBaker - Recipe Generator

BudderBaker is a Python-based tool that lets users create unique recipes for cannabis-infused products. The library interfaces with the Cannlytics API and OpenAI to produce these recipes.

## Usage

To generate a recipe, set the appropriate parameters in the data dictionary and POST this data to the specified API endpoint.

```py
# Create a recipe.
data = {
  'creativity': 0.420,
  'doses': [{'name': 'Terpinolene', 'value': 2.5, 'units': 'mg'}],
  'image_type': 'Water painting',
  'ingredients': ['coffee', 'milk', 'butter'],
  'product_name': 'Infused cannabis coffee',
  'public': True,
  'special_instructions': 'Morning coffee',
  'total_thc': 400,
  'total_cbd': 5,
  'units': 'mg',
}
url = 'https://cannlytics.com/api/ai/recipes'
response = session.post(url, json=data)
```
