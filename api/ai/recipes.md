
## BudderBaker - Recipe Generator

<!-- ```py
# Get a user's recipes.

``` -->

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
