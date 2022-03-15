"""
Lab Workflow
"""

from cannlytics.traceability import metrc

# Initialize a Metrc API client.
track = metrc.authorize('your-vendor-api-key', 'your-user-api-key')

# Post lab results.
track.post_lab_results([{...}, {...}])

# Get a tested package.
test_package = track.get_packages(label='abc')

# Get the tested package's lab result.
lab_results = track.get_lab_results(uid=test_package.id)
