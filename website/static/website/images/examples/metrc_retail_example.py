"""
Retail Workflow
"""

from cannlytics.traceability import metrc

# Initialize a Metrc API client.
track = metrc.authorize('your-vendor-api-key', 'your-user-api-key')

# Get a retail package.
package = track.get_packages(label='abc')

# Create a sales receipts.
track.create_receipts([{...}, {...}])

# Get recent receipts.
sales = track.get_receipts(action='active', start='2021-04-20')

# Update the sales receipt using.
sale = track.get_receipts(uid='420')
sale.total_price = 25
sale.update()
