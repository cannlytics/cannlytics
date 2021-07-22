# Analyses Endpoint `/api/analyses`

## Create an analysis

```py
data = {
    'analysis_id': 'hemp-analysis',
    'analytes': ['cbd', 'cbda', 'thc', 'thca'],
    'date': '2021-07-19',
    'initials': 'KLS',
    'key': 'hemp-analysis',
    'name': 'Hemp Analysis',
    'price': '',
    'public': False
}
org_id = 'test-company'
url = f'https://console.cannlytics.com/api/analyses?organization_id={org_id}'
response = requests.post(url, json=data, headers=HEADERS)
assert response.status_code == 200
print('Created:', response.json()['data'])
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': {
        'analysis_id': 'hemp-analysis',
        'analytes': ['cbd', 'cbda', 'thc', 'thca'],
        'date': '2021-07-19',
        'initials': 'KLS',
        'key': 'hemp-analysis',
        'name': 'Hemp Analysis',
        'price': '',
        'public': False
    }
}
```

## Get analyses

You can get analyses with the following:

```py
org_id = 'test-company'
url = f'https://console.cannlytics.com/api/?organization_id={org_id}'
response = requests.get(url, headers=HEADERS)
assert response.status_code == 200
data = response.json()['data']
print('Found:', len(data))
```

Expecting a response in the form:

```py
{
    'success': True,
    'data': [
          {
              'analysis_id': 'hemp-analysis',
              'analytes': ['cbd', 'cbda', 'thc', 'thca'],
              'date': '2021-07-19',
              'initials': 'KLS',
              'key': 'hemp-analysis',
              'name': 'Hemp Analysis',
              'price': '',
              'public': False
          }
    ]
}
```