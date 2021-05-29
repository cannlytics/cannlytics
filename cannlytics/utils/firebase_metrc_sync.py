"""
Sync Firebase and Metrc | Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: Sun May  2 15:07:00 2021
License: MIT License <https://opensource.org/licenses/MIT>

Maintaining Inventory in Sync
Packages can only leave a Facility's active inventory via Finishing, Discontinuing, and Outgoing Transfers. A Facility's active inventory is available through the /packages/v1/active endpoint.

When needing to sync your software's inventory with Metrc's, the following endpoints will enable you to accomplish that:

/packages/v1/active - provides the list of Packages currently considered "active" inventory.
/packages/v1/inactive - provides the list of Packages considered "inactive". Packages can only reach this status by being Finished or Discontinued.
And, finally, via the Outgoing Transfers:
First query /transfers/v1/outgoing.
Use the Id field from the returned objects as the {id} parameter in /transfers/v1/{id}/deliveries.
Please be mindful of rate limiting, as you must make one call per returned object, since the ID is part of the URL.
Then, use the Id field from the deliveries objects as the {id} parameter in /transfers/v1/delivery/{id}/packages.
Again, please keep in mind the rate limiting, as you must make one call per returned object, since the ID is part of the URL.
And, finally, the returned Package objects will include a PackageId and PackageLabel enabling your software to keep track of Packages leaving the active inventory.


Requesting Multiple Days' Data
Due to the existing Last Modified filter requirement, a single call cannot be made to request large amount of data. This restriction is enforced using a date range filter applied to the date and time of last modification.

Sometimes there is a need to request more data than allowed in a single request. In order to ensure no data is missed, the requests must be done in chronological order - start with older Last Modified date/times and move to more recent ones.

The Last Modified field can only logically move forward to a more recent date/time; it will never move backwards. This means that if you request data in reverse chronological order (newest first), you may happen to request the most recent data, followed by the next set, however, a change may occur causing a record to move within the most recent set (which was already requested). This would cause your software to miss that record, possibly until the next update.

"""


# TODO: Get historic data for a given user

# Limit by time, unless the user is a subscriber.


# Facilities

# Locations

# PAckages

# Items

# Plants

# Harvests

# Lab results

# Sales